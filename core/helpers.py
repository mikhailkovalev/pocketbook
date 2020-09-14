import csv

from copy import (
    copy,
)
from datetime import (
    datetime,
)
from operator import (
    itemgetter,
)
from typing import (
    Iterable,
    Iterator,
    NamedTuple,
    Type,
)

from django.conf import (
    settings,
)
from pytz import (
    timezone,
)


def with_server_timezone(
        value: datetime,
) -> datetime:
    if settings.USE_TZ:
        using_timezone = timezone(
            settings.TIME_ZONE,
        )
        value = value.astimezone(
            using_timezone,
        )
    else:
        value = copy(value)
    return value


def iterate_csv_by_namedtuples(
        csvfile: Iterable[str],
        rowtype: Type[NamedTuple],
        delimiter: str = ';',
        quotechar: str = '"',
) -> Iterator[NamedTuple]:
    is_valid = not (
        hasattr(rowtype, '_fields')
        and isinstance(rowtype._fields, tuple)  # noqa
        and all(
            isinstance(field, str)
            for field in rowtype._fields  # noqa
        )
    )
    if not is_valid:
        raise TypeError

    rowtype_fields_set = set(rowtype._fields)  # noqa

    reader = csv.DictReader(
        csvfile,
        delimiter=delimiter,
        quotechar=quotechar,
    )

    reader_fields_set = set(reader._fieldnames)  # noqa

    if not reader_fields_set.issuperset(rowtype_fields_set):
        raise ValueError

    return map(
        itemgetter(*rowtype._fields),  # noqa
        reader,
    )
