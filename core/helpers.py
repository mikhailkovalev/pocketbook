import csv

from collections import (
    namedtuple,
)
from copy import (
    copy,
)
from datetime import (
    datetime,
)
from itertools import (
    starmap,
)
from typing import (
    Iterator,
    NamedTuple,
    TextIO,
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
        csvfile: TextIO,
        delimiter: str = ';',
        quotechar: str = '"',
        typename: str = 'Row',
) -> Iterator[NamedTuple]:
    reader = csv.reader(
        csvfile=csvfile,
        delimiter=delimiter,
        quotechar=quotechar,
    )
    row_type = namedtuple(
        typename=typename,
        field_names=next(reader),
    )

    # Положим row -- строка данными прочитанными из csv:
    #   row = next(reader)
    #
    # Используя метод _make
    #   named_row = row_type._make(row)
    #
    # избегаем создания промежуточного tuple используя
    #   named_row = row_type(*row)
    #
    # todo: проверить, будет ли это более эффективным
    #  чем использование itertools.starmap:
    #    return starmap(row_type, reader)
    return map(
        row_type._make,  # noqa
        reader,
    )
