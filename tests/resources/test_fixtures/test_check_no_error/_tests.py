import logging

import pytest

logger = logging.getLogger(__name__)


# should be passed
# should be error
def test_teardown_error_if_not_handled_error_log():
    logger.error('Some Error')


# should be passed
# should be error
def test_teardown_error_if_not_handled_exception_log(test_exception):
    try:
        raise test_exception('Some Exception')
    except test_exception as exc:
        logger.exception(str(exc), exc_info=exc)


# should be failed
def test_fails_if_not_handled_exception(test_exception):
    raise test_exception('Another Exception')
