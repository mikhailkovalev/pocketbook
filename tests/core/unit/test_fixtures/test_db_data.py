import pathlib
from unittest.mock import ANY

import dirty_equals
import pytest
from django.contrib.auth.models import User

from core import test_helpers

test_users = pytest.mark.parametrize(
    [
        'db_data_filename',
        'expected_objs_data',
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
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('core', 'unit', 'test_fixtures', 'test_db_data', 'test_users')],
    )(
        test_helpers.test_db_objs(User, ('username',)),
    )
)
