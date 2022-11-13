import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db.utils import OperationalError


def test_db_available(
        transactional_db,
):
    # Просто запускаем команду: предполагается,
    # что при штатном запуске БД и так доступна,
    # поэтому больше никаких проверок.
    call_command('wait_db')


def test_db_not_available(
        transactional_db,
        connection_cursor_raises,
        assert_log_errors,
):
    with pytest.raises(CommandError):
        call_command('wait_db')

    assert_log_errors(
        'Intentionally raised',
        pytest.raises(OperationalError),
    )
