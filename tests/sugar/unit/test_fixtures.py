import pathlib
from datetime import datetime
from decimal import Decimal
from unittest.mock import ANY

import dirty_equals
import pytest
from django.contrib.auth.models import User

from core import test_helpers
from sugar.models import Record, SugarMetering, Meal, InsulinInjection


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
                    'id': 1,
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
                    'id': 2,
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
                    'id': 3,
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
                    'who_id': 1,
                    'when': datetime.fromisoformat('2021-05-16T11:00:00+03:00'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': 1,
                    'when': datetime.fromisoformat('2021-05-16T10:00:00+03:00'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': 2,
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


@pytest.mark.parametrize(
    'db_data_base_dir',
    [pathlib.Path('unit', 'test_fixtures', 'test_db_data_records')],
    indirect=True,
)
@pytest.mark.parametrize(
    [
        'db_data',
        'expected_log_errors',
        'expected_records',
        'expected_sugar_meterings',
        'expected_meals',
        'expected_injections',
    ],
    [
        [
            'test_attachments.yml',
            [],  # expected_log_errors
            # region expected_records
            [
                {
                    'id': 2,
                    'who_id': 1,
                    'when': datetime.fromisoformat('2024-03-16T10:00:00+03:00'),
                },
                {
                    'id': 3,
                    'who_id': 1,
                    'when': datetime.fromisoformat('2024-03-16T10:01:00+03:00'),
                },
            ],
            # endregion
            # region expected_sugar_meterings
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'sugar_level': Decimal('4.8'),
                    'pack_id': dirty_equals.IsPositiveInt,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 3,
                    'sugar_level': Decimal('5.2'),
                    'pack_id': dirty_equals.IsPositiveInt,
                },
            ],
            # endregion
            # region expected_meals
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'food_quantity': Decimal('1.0'),
                    'description': '',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'food_quantity': Decimal('1.1'),
                    'description': 'foo',
                },
            ],
            # endregion
            # region expected_injections
            [
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 3,
                    'insulin_quantity': 5,
                    'insulin_syringe_id': dirty_equals.IsPositiveInt,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 3,
                    'insulin_quantity': 6,
                    'insulin_syringe_id': dirty_equals.IsPositiveInt,
                },
            ],
            # endregion
        ],
    ],
    indirect=['db_data'],
)
def test_db_data_records(
    db_data,
    db_data_base_dir,

    assert_log_errors,
    model_to_dict,

    expected_log_errors,
    expected_records,
    expected_sugar_meterings,
    expected_meals,
    expected_injections,
):
    actual_records = Record.objects.order_by('id')
    assert len(actual_records) == len(expected_records)
    for idx, (actual, expected) in enumerate(zip(actual_records, expected_records)):
        actual_record_dict = model_to_dict(actual)
        assert sorted(actual_record_dict.keys()) == sorted(expected.keys()), \
            f'idx={idx!r}'
        for field_name, actual_value in actual_record_dict.items():
            assert actual_value == expected[field_name], \
                f'idx={idx!r}, field_name={field_name!r}'

    actual_meterings = SugarMetering.objects.order_by('id')
    assert len(actual_meterings) == len(expected_sugar_meterings)
    for idx, (actual, expected) in enumerate(zip(actual_meterings, expected_sugar_meterings)):
        actual_metering_dict = model_to_dict(actual)
        assert sorted(actual_metering_dict.keys()) == sorted(expected.keys()), \
            f'idx={idx!r}'
        for field_name, actual_value in actual_metering_dict.items():
            assert actual_value == expected[field_name], \
                f'idx={idx!r}, field_name={field_name!r}'

    actual_meals = Meal.objects.order_by('id')
    assert len(actual_meals) == len(expected_meals)
    for idx, (actual, expected) in enumerate(zip(actual_meals, expected_meals)):
        actual_meal_dict = model_to_dict(actual)
        assert sorted(actual_meal_dict.keys()) == sorted(expected.keys()), \
            f'idx={idx!r}'
        for field_name, actual_value in actual_meal_dict.items():
            assert actual_value == expected[field_name], \
                f'idx={idx!r}, field_name={field_name!r}'

    actual_injections = InsulinInjection.objects.order_by('id')
    assert len(actual_injections) == len(expected_injections)
    for idx, (actual, expected) in enumerate(zip(actual_injections, expected_injections)):
        actual_injection_dict = model_to_dict(actual)
        assert sorted(actual_injection_dict.keys()) == sorted(expected.keys()), \
            f'idx={idx!r}'
        for field_name, actual_value in actual_injection_dict.items():
            assert actual_value == expected[field_name], \
                f'idx={idx!r}, field_name={field_name!r}'

    assert_log_errors(*expected_log_errors)

