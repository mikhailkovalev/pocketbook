import pathlib
from datetime import datetime
from unittest.mock import ANY

import dirty_equals
import pytest
from django.contrib.auth.models import User

from core import test_helpers
from sugar.models import Record


@pytest.mark.parametrize(
    [
        'db_data',
        'expected_log_errors',
        'expected_records',
        'expected_users',
    ],
    [
        [
            'test_user_creation.yml',
            [],  # expected_log_errors
            [],  # expected_records
            # region expected_users
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('admin'),
                    'last_login': None,
                    'is_superuser': False,
                    'username': 'admin',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': True,
                    'is_active': True,
                    'date_joined': ANY,  # fixme: use freezer?
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('custom'),
                    'is_superuser': False,
                    'last_login': None,
                    'username': 'admin2',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': False,
                    'is_active': False,
                    'date_joined': ANY,  # fixme: use freezer?
                },
            ],
            # endregion
        ],
        [
            'test_many_default_users.yml',
            [
                'Multiple default users!',
                'Multiple default users!',
            ],
            [],  # expected_records
            # region expected_users
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('admin'),
                    'last_login': None,
                    'is_superuser': False,
                    'username': 'admin',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': False,
                    'is_active': True,
                    'date_joined': ANY,  # fixme: use freezer?
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('admin2'),
                    'is_superuser': False,
                    'last_login': None,
                    'username': 'admin2',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': False,
                    'is_active': True,
                    'date_joined': ANY,  # fixme: use freezer?
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('admin3'),
                    'is_superuser': False,
                    'last_login': None,
                    'username': 'admin3',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': False,
                    'is_active': True,
                    'date_joined': ANY,  # fixme: use freezer?
                },
            ],
            # endregion
        ],
        [
            'test_user_binding.yml',
            [],  # expected_log_errors
            # region expected_records
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': test_helpers.CheckWhose('admin'),
                    'when': datetime.fromisoformat('2021-05-16T11:00:00+03:00'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': test_helpers.CheckWhose('admin'),
                    'when': datetime.fromisoformat('2021-05-16T10:00:00+03:00'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': test_helpers.CheckWhose('admin2'),
                    'when': datetime.fromisoformat('2021-05-16T11:30:00+03:00'),
                },
            ],
            # endregion
            # region expected_users
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('admin'),
                    'last_login': None,
                    'is_superuser': True,
                    'username': 'admin',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': True,
                    'is_active': True,
                    'date_joined': ANY,  # fixme: use freezer?
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'password': test_helpers.CheckPassword('admin2'),
                    'is_superuser': False,
                    'last_login': None,
                    'username': 'admin2',
                    'first_name': '',
                    'last_name': '',
                    'email': '',
                    'is_staff': False,
                    'is_active': True,
                    'date_joined': ANY,  # fixme: use freezer?
                },
            ],
            # endregion
        ]
    ],
    indirect=[
        'db_data',
    ],
)
@pytest.mark.parametrize(
    'db_data_base_dir',
    [pathlib.Path('unit') / 'test_fixtures' / 'test_db_data_users'],
    indirect=True,
)
def test_db_data_users(
        db_data,
        db_data_base_dir,
        assert_log_errors,
        model_to_dict,
        expected_log_errors,
        expected_records,
        expected_users,
):
    actual_users = User.objects.order_by('username')
    assert len(actual_users) == len(expected_users)
    for idx, (actual, expected) in enumerate(zip(actual_users, expected_users)):
        actual_user_dict = model_to_dict(actual)
        assert sorted(actual_user_dict.keys()) == sorted(expected.keys()), \
            f'idx={idx!r}'
        for field_name, actual_value in actual_user_dict.items():
            assert actual_value == expected[field_name], \
                f'idx={idx!r}, field_name={field_name!r}'

    actual_records = Record.objects.order_by('who', '-when')
    assert len(actual_records) == len(expected_records)
    for idx, (actual, expected) in enumerate(zip(actual_records, expected_records)):
        actual_record_dict = model_to_dict(actual)
        assert sorted(actual_record_dict.keys()) == sorted(expected.keys()), \
            f'idx={idx!r}'
        for field_name, actual_value in actual_record_dict.items():
            assert actual_value == expected[field_name], \
                f'idx={idx!r}, field_name={field_name!r}'

    assert_log_errors(*expected_log_errors)


def test_db_data_records():
    pass
