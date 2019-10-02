import json
from collections import OrderedDict
from operator import itemgetter

from django.conf import settings
from django.http import HttpResponse

from core.export_helpers import (
    ExtractParams,
    OutAttrBuilder,
    prepare_objects,
    create_datetime_getter,
)

from .models import (
    Record,
    InsulinInjection,
    SugarMetering,
    Meal,
    Comment,
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
                getter_func=create_datetime_getter(
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
