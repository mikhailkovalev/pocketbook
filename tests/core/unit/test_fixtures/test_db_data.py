import pathlib
from unittest.mock import ANY

import dirty_equals
import pytest
from django.contrib.auth.models import User

from core import test_helpers


@pytest.mark.parametrize('db_data_base_dir', [pathlib.Path('core', 'unit', 'test_fixtures', 'test_db_data', 'test_users')])
@pytest.mark.parametrize(
    [
        'db_data_filename',
        'expected_users_data',
    ],
    [
        [
            'basic.yml',
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
        ],
    ],
)
def test_users(
        db_data,
        expected_users_data,
        model_to_dict,
):
    actual_users = User.objects.order_by('username')
    assert len(actual_users) == len(expected_users_data)
    for idx, (actual_user, expected_user_data) in enumerate(
        zip(actual_users, expected_users_data),
    ):
        actual_user_data = model_to_dict(actual_user)
        assert sorted(actual_user_data) == sorted(expected_user_data)
        for field_name, actual_value in actual_user_data.items():
            assert actual_value == expected_user_data[field_name], f'idx={idx!r}; field_name={field_name!r}'
