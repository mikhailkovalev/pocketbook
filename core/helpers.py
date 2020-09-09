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
    Iterable,
    Iterator,
    NamedTuple,
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

# TODO: Вместо вызова namedtuple внутри функции, лучше
#  принимать его как аргумент. Далее можно проверять,
#  что атрибуты переданного типа являются подмножеством
#  колонок csv-файла. Далее создаём генератор
#  namedtuple-ов из строк, учитывая требуемый порядок
#  и возвращаем его
def iterate_csv_by_namedtuples(
        csvfile: Iterable[str],
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

    return starmap(
        row_type,
        reader,
    )
