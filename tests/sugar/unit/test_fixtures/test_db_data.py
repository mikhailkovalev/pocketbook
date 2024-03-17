import pathlib
from datetime import date, datetime
from decimal import Decimal
from typing import Type, Sequence

import dirty_equals
import pytest
from django.db.models import Model

from core import test_helpers
from sugar.models import Record, SugarMetering, Meal, InsulinInjection, TestStripPack, InsulinKind, InsulinSyringe, Comment


def _test_db_objs(
    model: Type[Model],
    ordering: Sequence[str],
):
    def __test_db_objs(db_data, db_data_filename, expected_objs_data, model_to_dict):
        actual_objs = model.objects.order_by(*ordering)
        assert len(actual_objs) == len(expected_objs_data)
        for idx, (actual_obj, expected_obj_data) in enumerate(
            zip(actual_objs, expected_objs_data),
        ):
            actual_obj_data = model_to_dict(actual_obj)
            assert sorted(actual_obj_data) == sorted(expected_obj_data)
            for field_name, actual_value in actual_obj_data.items():
                assert actual_value == expected_obj_data[field_name], \
                    f'idx={idx!r}; field_name={field_name!r}'

    return __test_db_objs


test_records = pytest.mark.parametrize(
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
                    'who_id': 1,
                    'when': datetime.fromisoformat('2023-03-17T11:00:00.000+03:00'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': 1,
                    'when': datetime.fromisoformat('2023-03-17T10:00:00.000+03:00'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'who_id': 2,
                    'when': datetime.fromisoformat('2023-03-17T10:30:00.000+03:00'),
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_records')],
    )(
        _test_db_objs(Record, ('who', '-when')),
    )
)

test_packs = pytest.mark.parametrize(
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
                    'whose_id': 1,
                    'volume': 50,
                    'opening': date(2024, 3, 10),
                    'expiry_plan': date(2024, 3, 17),
                    'expiry_actual': None,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'whose_id': 1,
                    'volume': 50,
                    'opening': date(2024, 3, 1),
                    'expiry_plan': date(2024, 3, 7),
                    'expiry_actual': date(2024, 3, 10),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'whose_id': 2,
                    'volume': 25,
                    'opening': date(2024, 2, 29),
                    'expiry_plan': date(2024, 3, 6),
                    'expiry_actual': None,
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_packs')],
    )(
        _test_db_objs(TestStripPack, ('whose', '-opening')),
    )
)

test_meterings = pytest.mark.parametrize(
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
                    'record_id': 5,
                    'pack_id': 3,
                    'sugar_level': Decimal('6.5'),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 4,
                    'pack_id': 2,
                    'sugar_level': Decimal('4.8'),
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_meterings')],
    )(
        _test_db_objs(SugarMetering, ('record__who_id', '-record__when')),
    )
)

test_insulin_kinds = pytest.mark.parametrize(
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
                    'name': 'TestInsulinKind1',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'name': 'TestInsulinKind2',
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_insulin_kinds')],
    )(
        _test_db_objs(InsulinKind, ('name',)),
    )
)

test_insulin_syringes = pytest.mark.parametrize(
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
                    'insulin_mark_id': 3,
                    'whose_id': 1,
                    'volume': 300,
                    'opening': date(2024, 3, 15),
                    'expiry_plan': date(2024, 3, 29),
                    'expiry_actual': None,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'insulin_mark_id': 4,
                    'whose_id': 1,
                    'volume': 450,
                    'opening': date(2024, 3, 3),
                    'expiry_plan': date(2024, 3, 25),
                    'expiry_actual': date(2024, 3, 23),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'insulin_mark_id': 3,
                    'whose_id': 1,
                    'volume': 300,
                    'opening': date(2024, 3, 1),
                    'expiry_plan': date(2024, 3, 15),
                    'expiry_actual': date(2024, 3, 15),
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'insulin_mark_id': 3,
                    'whose_id': 2,
                    'volume': 300,
                    'opening': date(2024, 3, 2),
                    'expiry_plan': date(2024, 3, 17),
                    'expiry_actual': None,
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_insulin_syringes')],
    )(
        _test_db_objs(InsulinSyringe, ('whose', '-opening')),
    )
)

test_insulin_injections = pytest.mark.parametrize(
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
                    'record_id': 8,
                    'insulin_syringe_id': 5,
                    'insulin_quantity': 6,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 8,
                    'insulin_syringe_id': 6,
                    'insulin_quantity': 20,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 7,
                    'insulin_syringe_id': 5,
                    'insulin_quantity': 2,
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 7,
                    'insulin_syringe_id': 4,
                    'insulin_quantity': 4,
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_insulin_injections')],
    )(
        _test_db_objs(InsulinInjection, ['record__who_id', '-record__when', 'insulin_quantity']),
    )
)

test_meals = pytest.mark.parametrize(
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
                    'record_id': 3,
                    'food_quantity': Decimal('2.3'),
                    'description': 'Test2',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 3,
                    'food_quantity': Decimal('3.0'),
                    'description': 'Test3',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'food_quantity': Decimal('0.9'),
                    'description': 'Test1',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'food_quantity': Decimal('5.1'),
                    'description': '',
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_meals')],
    )(
        _test_db_objs(Meal, ['record__who_id', '-record__when', 'food_quantity']),
    )
)

test_comments = pytest.mark.parametrize(
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
                    'record_id': 3,
                    'content': 'Buz',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'content': 'Bar',
                },
                {
                    'id': dirty_equals.IsPositiveInt,
                    'record_id': 2,
                    'content': 'Foo',
                },
            ],
        ],
    ],
)(
    pytest.mark.parametrize(
        'db_data_base_dir',
        [pathlib.Path('sugar', 'unit', 'test_fixtures', 'test_db_data', 'test_comments')],
    )(
        _test_db_objs(Comment, ['record__who_id', '-record__when', 'content']),
    )
)
