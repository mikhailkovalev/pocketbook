import csv

from collections import (
    namedtuple,
)
from copy import (
    copy,
)
from datetime import (
    date,
    datetime,
    time,
)
from itertools import (
    starmap,
)
from typing import (
    Iterator,
    NamedTuple,
    Optional,
    TextIO,
    Type,
    Union,
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


class AbleToVerbolizeDateTimeAttrsMixin:
    def _get_verbose_datetime(
            self,
            attr: str,
            fmt: str,
            src_type: Union[Type[date], Type[time]],
    ) -> Optional[str]:
        assert hasattr(self, attr)
        date_value = getattr(self, attr)
        if date_value is None:
            return None
        assert isinstance(date_value, src_type)
        return date_value.strftime(fmt)

    def get_verbose_date(
            self,
            attr: str,
            fmt: str = '%Y-%m-%d',
    ) -> Optional[str]:
        return self._get_verbose_datetime(attr, fmt, date)

    def get_verbose_datetime(
            self,
            attr: str,
            fmt: str = '%Y-%m-%d %H:%M',
    ) -> Optional[str]:
        return self._get_verbose_datetime(attr, fmt, datetime)


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

    return starmap(
        row_type,
        reader,
    )
