import json
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

from .forms import (
    ListViewForm,
)
from .helpers import (
    TIME_LABEL_FORMAT,
    TRUNC_TYPES,
    AttachmentMeta,
    SliceParams,
    export_attachments,
    get_injections_verbose_data,
    get_meal_verbose_data,
    get_sugar_verbose_data,
    slice_records,
)
from .models import (
    InsulinInjection,
    Meal,
    Record,
    SugarMetering,
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
    groupping = request.POST.get('groupping')

    page_size = settings.DEFAULT_PAGE_SIZE  # FIXME: get it from request

    page_number = 1
    try:
        page_number = int(request.POST.get('page_number'))
    except ValueError:
        pass

    records = Record.objects.filter(
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
        target_page_number=page_number,
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
                'insulin_syringe__insulin_mark',
                'insulin_syringe__insulin_mark__name',
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

    # todo: Написать класс-обёртку для columns,
    #  чтобы при каждом редактировании проверялась
    #  уникальность data_index-ов (в дебаге) с печатью
    #  сообщений об ошибках в лог.
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

    response_data = dict(
        rows=response_rows,
        columns=columns,
        total_rows_count=slice_params.total_rows_count,
        total_pages_count=slice_params.total_pages_count,
        page_number=slice_params.page_number,
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
