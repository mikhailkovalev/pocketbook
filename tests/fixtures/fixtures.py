import contextlib
import itertools
import logging
import os.path
import pathlib
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
    List,
    Optional,
    TYPE_CHECKING,
)
from unittest import mock

import freezegun
import pytest
import pytz
import yaml
from _pytest.python_api import RaisesContext  # noqa
from django.apps import apps
from django.conf import (
    settings,
)

if TYPE_CHECKING:
    from django.db.models import (
        Model,
    )


@pytest.fixture
def tz():
    return pytz.timezone(settings.TIME_ZONE)


@pytest.fixture
def create_datetime(tz) -> Callable[[str], datetime]:
    # TODO: убрать и использовать datetime.fromisoformat
    #  после обновления python на 3.7+
    def _create_datetime(raw: str):
        return tz.localize(
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


@pytest.fixture(autouse=True)
def check_no_errors(caplog):
    yield
    for when in ('setup', 'call'):
        errors = [
            record.message
            for record in caplog.get_records(when)
            if record.levelno >= logging.ERROR
        ]
        if errors:
            pytest.fail(f'Unexpected errors: {errors!r}')


@pytest.fixture
def assert_log_errors(caplog):
    def _assert_log_errors(*expected_errors):
        expected_error_messages = []
        expected_exceptions = []
        for error in expected_errors:
            if isinstance(error, str):
                expected_error_messages.append(error)
                expected_exceptions.append(None)
            elif isinstance(error, RaisesContext):
                assert expected_exceptions[-1] is None
                expected_exceptions[-1] = error
            else:
                raise NotImplementedError

        all_records_iterator = itertools.chain(
            caplog.get_records('setup'),
            caplog.get_records('call'),
        )
        error_records = [
            record
            for record in all_records_iterator
            if record.levelno >= logging.ERROR
        ]

        actual_error_messages = [record.message for record in error_records]
        assert actual_error_messages == expected_error_messages

        for record, expected_exception in zip(
            error_records,
            expected_exceptions,
        ):
            if expected_exception is None:
                continue
            with expected_exception:
                raise record.exc_info[1]

        for when in ('setup', 'call'):
            del caplog.get_records(when)[:]
        caplog.clear()

    return _assert_log_errors


@pytest.fixture
def test_exception():
    class TestException(Exception):
        pass

    return TestException


@pytest.fixture
def db_data_base_dir():
    raise NotImplementedError


@pytest.fixture
def db_data_filename() -> str:
    raise NotImplementedError  # должно переопределяться


@pytest.fixture
def db_data_path(db_data_base_dir: pathlib.Path, db_data_filename: str, resources) -> pathlib.Path:
    return pathlib.Path(resources) / db_data_base_dir / db_data_filename


@pytest.fixture
def db_data_raw(db_data_path: pathlib.Path) -> Optional[List[Dict[str, Any]]]:
    with open(db_data_path, 'rt', encoding='utf-8') as db_data_file:
        return yaml.load(db_data_file, Loader=yaml.FullLoader)


@pytest.fixture
def db_data_constructors(create_user) -> Dict[str, Callable]:
    return {
        settings.AUTH_USER_MODEL: create_user,
    }


@pytest.fixture
def db_data(transactional_db, db_data_raw: Optional[List[Dict[str, Any]]], db_data_constructors):
    for obj_raw in db_data_raw or ():
        model_name = obj_raw.pop('model')
        constructor = db_data_constructors.get(model_name, apps.get_model(model_name).objects.create)
        constructor(**obj_raw)


@pytest.fixture
def frozen_time() -> Optional[str]:
    return None


@pytest.fixture
def freeze_time(frozen_time):
    if frozen_time is None:
        context_manager = contextlib.nullcontext()
    else:
        context_manager = freezegun.freeze_time(frozen_time)

    with context_manager as frozen_time_:
        yield frozen_time_
