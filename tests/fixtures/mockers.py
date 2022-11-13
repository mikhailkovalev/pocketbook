"""
Fixtures that mock something
"""
import pytest
from django.db.utils import OperationalError


@pytest.fixture
def connection_cursor_raises(
        mocker,
):
    def _raise(*args, **kwargs):
        raise OperationalError('Intentionally raised')

    mocker.patch(
        'django.db.backends.base.base.BaseDatabaseWrapper.cursor',
        side_effect=_raise,
    )
