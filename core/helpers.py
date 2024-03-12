import operator
import typing
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


def _get_datetime_display(
        value: Optional[date],
        fmt: str,
) -> Optional[str]:
    if value is None:
        return None
    return value.strftime(fmt)


def get_date_display(
        value: Optional[date],
        fmt: str = '%Y-%m-%d',
) -> Optional[str]:
    return _get_datetime_display(value, fmt)


def get_datetime_display(
        value: Optional[datetime],
        fmt: str = '%Y-%m-%d %H:%M',
) -> Optional[str]:
    return _get_datetime_display(value, fmt)


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


T = typing.TypeVar('T')


def iter_pairs(
    iterable: typing.Iterable[T],
) -> typing.Iterator[typing.Tuple[T, T]]:
    iterator = iter(iterable)
    try:
        prev_item = next(iterator)
    except StopIteration:
        return

    for item in iterator:
        yield prev_item, item
        prev_item = item


def is_sorted(
    iterable: typing.Iterable[T],
    key: typing.Optional[typing.Callable[[T], typing.Any]] = None,
    reversed: bool = False,
) -> bool:
    if reversed:
        def is_not_ordered(_prev_item, _current_item):
            return _prev_item < _current_item
    else:
        def is_not_ordered(_prev_item, _current_item):
            return _current_item < _prev_item

    if key is None:
        iterator = iter(iterable)
    else:
        iterator = map(key, iterable)

    for prev_item, current_item in iter_pairs(iterator):
        if is_not_ordered(prev_item, current_item):
            return False

    return True


def numpy_interp(
    dest_args,
    source_args,
    source_values,
):
    source_pairs = list(zip(source_args, source_values))
    if not is_sorted(source_args):
        source_pairs.sort(key=operator.itemgetter(0))

    scales = []
    offsets = []

    for (prev_arg, prev_value), (arg, value) in iter_pairs(source_pairs):
        factor = 1 / (arg - prev_arg)
        scales.append((value - prev_value) * factor)
        offsets.append((arg*prev_value - prev_arg*value) * factor)

    if not is_sorted(dest_args):
        ids_by_dest_arg = {arg: idx for idx, arg in enumerate(dest_args)}
        dest_args = sorted(dest_args)
    else:
        ids_by_dest_arg = None

    interval_idx = 0
    dest_values = []
    for dest_arg in dest_args:
        while True:
            if interval_idx >= len(scales)-1 or dest_arg <= source_args[interval_idx+1]:
                break
            interval_idx += 1
        dest_values.append(scales[interval_idx]*dest_arg + offsets[interval_idx])

    if ids_by_dest_arg is not None:
        dest_pairs = list(zip(dest_args, dest_values))
        dest_pairs.sort(key=lambda pair: ids_by_dest_arg.get(pair[0]))
        dest_values = [pair[1] for pair in dest_pairs]

    return dest_values

