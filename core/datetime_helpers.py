from copy import copy
from datetime import datetime
from pytz import timezone

from django.conf import settings


def with_server_timezone(
        value: datetime) -> datetime:
    if settings.USE_TZ:
        using_timezone = timezone(
            settings.TIME_ZONE)
        value = value.astimezone(
            using_timezone)
    else:
        value = copy(value)
    return value
