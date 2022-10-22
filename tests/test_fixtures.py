import pathlib
import typing as t
import logging

import pytest


logger = logging.getLogger(__name__)


@pytest.fixture
def log_error():
    def _log_error():
        logger.error('Some Error')
    return _log_error


@pytest.fixture
def log_exception(test_exception):
    def _log_exception():
        try:
            raise test_exception('Some Exception')
        except test_exception as exc:
            logger.error(str(exc), exc_info=exc)
    return _log_exception


@pytest.fixture
def error_log_args():
    return ['Some Error']


@pytest.fixture
def exception_log_args(
        test_exception,
):
    return ['Some Exception', pytest.raises(test_exception)]


@pytest.mark.parametrize(
    [
        'func',
        'fixture_args',
    ],
    [
        [
            pytest.lazy_fixture('log_error'),  # noqa
            pytest.lazy_fixture('error_log_args'),  # noqa
        ],
        [
            pytest.lazy_fixture('log_exception'),  # noqa
            pytest.lazy_fixture('exception_log_args'),  # noqa
        ],
    ],
)
def test_assert_log_errors(
        assert_log_errors,
        func: t.Callable,
        fixture_args,
):
    func()
    assert_log_errors(*fixture_args)


@pytest.fixture
def _pytest_ini(resources):
    return pathlib.Path(
        resources,
        'test_fixtures',
        'test_check_no_error',
        '_pytest.ini',
    ).read_text()


@pytest.fixture
def _conftest(resources):
    return pathlib.Path(
        resources,
        'test_fixtures',
        'test_check_no_error',
        '_conftest.py',
    ).read_text()


@pytest.fixture
def _tests(resources):
    return pathlib.Path(
        resources,
        'test_fixtures',
        'test_check_no_error',
        '_tests.py',
    ).read_text()


def test_check_no_error(
        _pytest_ini,
        _conftest,
        _tests,

        testdir,
        assert_log_errors,
):
    testdir.makeini(_pytest_ini)
    testdir.makeconftest(_conftest)
    testdir.makepyfile(_tests)
    result = testdir.runpytest()
    result.assert_outcomes(passed=2, errors=2, failed=1)
    assert_log_errors(
        'Some Error',

        # нельзя использовать фикстуру test_exception,
        # потому что внутри `runpytest` инициализируются
        # свои фикстуры и `test_exception` созданный там
        # будет отличаться от здешнего `test_exception`
        'Some Exception',
        pytest.raises(Exception),
    )
