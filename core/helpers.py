from copy import (
    copy,
)
from datetime import (
    date,
    datetime,
)
from time import (
    perf_counter,
    perf_counter_ns,
)
from typing import (
    Optional,
)

from django.conf import (
    settings,
)
from django.db.models import (
    Sum,
)
from django.db.models.functions import (
    Coalesce,
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


def _get_verbose_datetime(
        value: Optional[date],
        fmt: str,
) -> Optional[str]:
    if value is None:
        return None
    return value.strftime(fmt)


def get_verbose_date(
        value: Optional[date],
        fmt: str = '%Y-%m-%d',
) -> Optional[str]:
    return _get_verbose_datetime(value, fmt)


def get_verbose_datetime(
        value: Optional[datetime],
        fmt: str = '%Y-%m-%d %H:%M',
) -> Optional[str]:
    return _get_verbose_datetime(value, fmt)


def NumericSum(*args, **kwargs):
    return Coalesce(Sum(*args, **kwargs), 0)


# noinspection PyPep8Naming
class track_time:
    def __init__(self, use_ns: bool = False):
        if use_ns:
            self._time_func = perf_counter_ns
        else:
            self._time_func = perf_counter

        self._start = None
        self._finish = None

    def __enter__(self):
        self._start = self._time_func()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._finish = self._time_func()

    @property
    def elapsed_time(self):
        return self._finish - self._start
