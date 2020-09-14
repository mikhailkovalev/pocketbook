import csv

from copy import (
    copy,
)
from datetime import (
    date,
    datetime,
    time,
)
from operator import (
    itemgetter,
)
from typing import (
    Iterable,
    Iterator,
    NamedTuple,
    Optional,
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
        # fixme: разве должны возвращаться обычные tuple?
        itemgetter(*rowtype._fields),  # noqa
        reader,
    )
