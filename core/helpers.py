from copy import (
    copy,
)
from datetime import (
    date,
    datetime,
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


def delattr_if_exists(obj, name):
    """
    В отличие от обычного `delattr` не бросает
    `AttributeError`, если пытаемся удалить
    атрибут, которого нет у объекта
    """
    if hasattr(obj, name):
        delattr(obj, name)
