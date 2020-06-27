import json
from collections import (
    OrderedDict,
)
from datetime import (
    datetime,
)
from itertools import (
    groupby,
)
from operator import (
    itemgetter,
)
from typing import (
    Any,
    Callable,
    Dict,
    List,
)

from django.conf import (
    settings,
)
from django.contrib.auth.decorators import (
    login_required,
)
from django.db.models import (
    DateTimeField,
)
from django.db.models.functions import (
    Trunc,
)
from django.http import (
    HttpResponse,
)
from django.shortcuts import (
    render,
)
from django.views.decorators.csrf import (
    requires_csrf_token,
)
from pytz import (
    timezone,
)

from core.export_helpers import (
    ExtractParams,
    OutAttrBuilder,
    create_datetime_as_str_getter,
    prepare_objects,
)

from .forms import (
    ListViewForm,
)
from .helpers import (
    TIME_LABEL_FORMAT,
    TRUNC_TYPES,
    AttachmentMeta,
    SliceParams,
    export_attachments,
    get_filter_by_period,
    get_injections_verbose_data,
    get_meal_verbose_data,
    get_sugar_verbose_data,
    slice_records,
)
from .models import (
    Comment,
    InsulinInjection,
    Meal,
    Record,
    SugarMetering,
)


def get_records(request):
    records_on_page = 5

    raw_records = Record.objects.filter(
        # by who
    ).values(
        'id',
        'when',
    )

    # FIXME: Учитывать параметры пагинации из
    #  request.
    raw_records = raw_records[:records_on_page]

    prepared_records = prepare_objects(
        raw_records,
        (
            OutAttrBuilder(
                attr_name='id',
            ),
            OutAttrBuilder(
                attr_name='when',
                getter_func=create_datetime_as_str_getter(
                    attr_name='when',
                    fmt='%Y-%m-%d %H:%M',
                ),
            ),
        ),
    )
    records_by_id = OrderedDict((
        (record['id'], record)
        for record in prepared_records
    ))

    records_ids = tuple(records_by_id.keys())

    attachments_export_params = {
        'sugar_meterings': ExtractParams(
            model=SugarMetering,
            raw_values=(
                'sugar_level',
            ),
        ),
        'meals': ExtractParams(
            model=Meal,
            raw_values=(
                'food_quantity',
            ),
        ),
        'insulin_injections': ExtractParams(
            model=InsulinInjection,
            raw_values=(
                'insulin_mark__name',
                'insulin_quantity',
            ),
            out_attrs_builders=(
                OutAttrBuilder(
                    attr_name='record_id',
                ),
                OutAttrBuilder(
                    attr_name='insulin_mark',
                    getter_func=itemgetter('insulin_mark__name'),
                ),
                OutAttrBuilder(
                    attr_name='insulin_quantity',
                ),
            )
        ),
        'comments': ExtractParams(
            model=Comment,
            raw_values=(
                'content',
            ),
        ),
    }

    for attachment_name in attachments_export_params:
        for record in records_by_id.values():
            record[attachment_name] = []

    for attachment_name, extract_params in attachments_export_params.items():
        raw_attachments = extract_params.model.objects.filter(
            record_id__in=records_ids,
        ).values(
            'record_id',
            *extract_params.raw_values,
        )
        prepared_attachments = prepare_objects(
            raw_attachments,
            extract_params.out_attrs_builders,
        )
        for attachment in prepared_attachments:
            records_by_id[
                attachment['record_id']
            ][
                attachment_name
            ].append(
                attachment,
            )

    dumps_kwargs = {}
    if settings.DEBUG:
        dumps_kwargs.update(
            indent=4,
            ensure_ascii=False,
        )

    result = json.dumps(
        tuple(records_by_id.values()),
        **dumps_kwargs,
    )

    return HttpResponse(
        result.encode('utf-8'),
        content_type='application/json',
    )


def list_view(request):
    list_view_form = ListViewForm()
    context = dict(
        list_view_form=list_view_form,
    )
    return render(
        request=request,
        template_name='sugar/list.html',
        context=context,
    )


@requires_csrf_token
@login_required
def rows_view(request, *args, **kwargs):
    period = request.POST.get('period')
    groupping = request.POST.get('groupping')

    page_size = 200  # FIXME: get it from request
    page_number = 1  # FIXME: get it from request

    records = Record.objects.filter(
        get_filter_by_period(period),
        who=request.user.id,
    ).annotate(
        time_label=Trunc(
            expression='when',
            kind=TRUNC_TYPES[groupping],
            output_field=DateTimeField(),
            tzinfo=timezone(settings.TIME_ZONE),
        ),
        localized_when=Trunc(
            expression='when',
            kind='second',
            output_field=DateTimeField(),
            tzinfo=timezone(settings.TIME_ZONE),
        ),
    )

    slice_params: SliceParams = slice_records(
        records=records,
        page_number=page_number,
        page_size=page_size,
    )

    records = slice_params.records.values(
        'id',
        'when',
        'localized_when',
        'time_label',
    )

    export_attachments(
        records,
        AttachmentMeta(
            model=Meal,
            set_name='meals',
            fk_name='record',
            filter_=slice_params.slice_filter,
            export_values=(
                'food_quantity',
            ),
        ),
        AttachmentMeta(
            model=InsulinInjection,
            set_name='injections',
            fk_name='record',
            filter_=slice_params.slice_filter,
            export_values=(
                'insulin_mark',
                'insulin_mark__name',
                'insulin_quantity',
            ),
        ),
        AttachmentMeta(
            model=SugarMetering,
            set_name='sugar_meterings',
            fk_name='record',
            filter_=slice_params.slice_filter,
            export_values=(
                'sugar_level',
            ),
        ),
    )

    columns: List[Dict[str, str]] = [
        dict(
            data_index='time_label',
            header='Дата/время',
        ),
    ]
    get_verbose_time_label: Callable[[datetime], str] = TIME_LABEL_FORMAT[groupping]
    key_func: Callable[[Dict[str, Any]], Any] = itemgetter('time_label')

    response_rows: List[Dict[str, Any]] = [
        {
            'time_label': get_verbose_time_label(time_label),
        }
        for time_label, _ in groupby(records, key_func)
    ]

    get_sugar_verbose_data(
        records,
        columns,
        response_rows,
        key_func,
        groupping,
    )
    get_meal_verbose_data(
        records,
        columns,
        response_rows,
        key_func,
    )
    get_injections_verbose_data(
        records,
        columns,
        response_rows,
        key_func,
    )

    # for time_label, records_group in groupby(records, itemgetter('time_label')):
    #     row: Dict[str, Any] = {
    #         'time_label': get_verbose_time_label(time_label),
    #         'meal': 0,
    #         'sugar_level': None,
    #     }
    #     response_rows.append(row)
    #     for record in records_group:
    #         # region sugar
    #         # done: по time_label определять datetime-границ этого промежутка
    #         #       helpers.TIME_LABEL_ENDS
    #         # done: интегрировать функцию уровня сахара по заданным границам
    #         #       helpers.TrapezoidalSugarAverager
    #         # endregion
    #
    #         for meal_info in record['meals']:
    #             row['meal'] += meal_info['food_quantity']
    #
    #         for injection_info in record['injections']:
    #             data_index = insulin_data_indices.get(
    #                 injection_info['insulin_mark'],
    #             )
    #             if data_index is None:
    #                 mark_id = injection_info['insulin_mark']
    #                 data_index = 'insulin_{mark}'.format(
    #                     mark=mark_id,
    #                 )
    #                 columns.append(dict(
    #                     header=injection_info['insulin_mark__name'],
    #                     data_index=data_index,
    #                 ))
    #                 insulin_data_indices[mark_id] = data_index
    #             if data_index in row:
    #                 row[data_index] += injection_info['insulin_quantity']
    #             else:
    #                 row[data_index] = injection_info['insulin_quantity']
    #
    # for row in response_rows:
    #     row['meal'] = str(row['meal'])

    # todo: упорядочить колонки с инсулином
    response_data = dict(
        rows=response_rows,
        columns=columns,
        total_rows_count=slice_params.total_rows_count,
        first_shown=slice_params.first_shown,
        last_shown=slice_params.last_shown,
    )
    dumps_kwargs: Dict[str, Any]
    if settings.DEBUG:
        dumps_kwargs = dict(
            ensure_ascii=False,
            indent=4,
        )
    else:
        dumps_kwargs = dict(
            ensure_ascii=True,
        )

    return HttpResponse(json.dumps(
        response_data,
        **dumps_kwargs,
    ))
