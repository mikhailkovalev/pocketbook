"""
Fixtures that override settings params
"""

import pytest


@pytest.fixture(autouse=True)
def setup_test_settings(
        settings,
        wait_db_timeout,
):
    settings.DEBUG = True
    settings.WAIT_DB_TIMEOUT = wait_db_timeout


@pytest.fixture(params=[1])
def wait_db_timeout(request):
    return request.param
