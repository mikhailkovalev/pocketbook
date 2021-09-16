import os.path
from datetime import (
    datetime,
)
from operator import (
    attrgetter,
)
from typing import (
    Any,
    Callable,
    Dict,
    TYPE_CHECKING,
)

import pytest
import pytz
from django.conf import (
    settings,
)

if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )


@pytest.fixture
def timezone():
    return pytz.timezone(settings.TIME_ZONE)


@pytest.fixture
def create_datetime(timezone) -> Callable[[str], datetime]:
    # TODO: убрать и использовать datetime.fromisoformat
    #  после обновления python на 3.7+
    def _create_datetime(raw: str):
        return timezone.localize(
            datetime.strptime(raw, '%Y-%m-%dT%H:%M:%S'),
        )
    return _create_datetime


@pytest.fixture
def model_to_dict() -> Callable[["Model"], Dict[str, Any]]:
    def _model_to_dict(obj: "Model") -> Dict[str, Any]:
        attrs = map(
            attrgetter('attname'),
            obj._meta.fields,  # noqa
        )
        return {
            attr: getattr(obj, attr)
            for attr in attrs
        }
    return _model_to_dict


@pytest.fixture
def resources() -> str:
    return os.path.abspath(os.path.join(
        __file__,
        os.path.pardir,
        os.path.pardir,
        'resources',
    ))
