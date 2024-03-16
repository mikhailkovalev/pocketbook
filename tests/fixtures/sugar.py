import logging
import pathlib
from datetime import (
    date,
)
from decimal import (
    Decimal,
)
from typing import (
    Optional,
)

import pytest
import yaml

from sugar.models import (
    Comment,
    InsulinInjection,
    InsulinKind,
    InsulinSyringe,
    Meal,
    Record,
    SugarMetering,
    TestStripPack,
)


logger = logging.getLogger(__name__)


@pytest.fixture
def create_comment():
    def _create_comment(
            record: Record,
            content: str,
    ):
        return Comment.objects.create(
            record=record,
            content=content,
        )

    return _create_comment


@pytest.fixture
def create_meal():
    def _create_meal(
            record: Record,
            food_quantity: Decimal,
            description: str = '',
    ):
        meal = Meal.objects.create(
            record=record,
            food_quantity=food_quantity,
            description=description,
        )
        return meal

    return _create_meal


@pytest.fixture
def create_insulin_kind():
    def _create_insulin_kind(name):
        insulin_kind, _ = InsulinKind.objects.get_or_create(
            name=name,
        )
        return insulin_kind

    return _create_insulin_kind


@pytest.fixture
def create_insulin_syringe(
        create_insulin_kind,
):
    def _create_insulin_syringe(
            whose,
            volume: int,
            opening: date,
            expiry_plan: date,
            expiry_actual: Optional[date] = None,
            **kwargs,
            # insulin_mark: InsulinKind,
    ):
        try:
            insulin_mark = kwargs['insulin_mark']
        except KeyError:
            insulin_mark = create_insulin_kind(
                name='Aspart',
            )

        insulin_syringe, _ = InsulinSyringe.objects.get_or_create(
            whose=whose,
            volume=volume,
            opening=opening,
            expiry_plan=expiry_plan,
            expiry_actual=expiry_actual,
            insulin_mark=insulin_mark,
        )
        return insulin_syringe

    return _create_insulin_syringe


@pytest.fixture
def create_insulin_injection(
        create_insulin_syringe,
):
    def _create_insulin_injection(
            record: Record,
            insulin_quantity: int,
            **kwargs,
            # insulin_syringe: InsulinSyringe,
    ):
        try:
            insulin_syringe = kwargs['insulin_syringe']
        except KeyError:
            insulin_syringe = create_insulin_syringe(
                whose=record.who,
                volume=300,
                opening=date(
                    year=2021,
                    month=5,
                    day=7,
                ),
                expiry_plan=date(
                    year=2021,
                    month=5,
                    day=20,
                ),
            )
        insulin_injection = InsulinInjection.objects.create(
            record=record,
            insulin_syringe=insulin_syringe,
            insulin_quantity=insulin_quantity,
        )
        return insulin_injection

    return _create_insulin_injection


@pytest.fixture
def create_test_strip_pack():
    def _create_test_strip_pack(
            whose,
            volume,
            opening,
            expiry_plan,
            expiry_actual=None,
    ):
        test_strip_pack, _ = TestStripPack.objects.get_or_create(
            whose=whose,
            volume=volume,
            opening=opening,
            expiry_plan=expiry_plan,
            expiry_actual=expiry_actual,
        )
        return test_strip_pack

    return _create_test_strip_pack


@pytest.fixture
def create_sugar_metering(
        create_test_strip_pack,
):
    def _create_sugar_metering(
            record: Record,
            sugar_level: Decimal,
            **kwargs,
            # pack: TestStripPack,
    ):
        try:
            pack = kwargs['pack']
        except KeyError:
            pack = create_test_strip_pack(
                whose=record.who,
                volume=50,
                opening=date(
                    year=2021,
                    month=5,
                    day=5,
                ),
                expiry_plan=date(
                    year=2021,
                    month=5,
                    day=13,
                ),
            )

        sugar_metering = SugarMetering.objects.create(
            record=record,
            pack=pack,
            sugar_level=sugar_level,
        )
        return sugar_metering

    return _create_sugar_metering


@pytest.fixture
def create_record(
        create_datetime,
        create_meal,
        create_sugar_metering,
        create_insulin_injection,
        create_comment,
):
    def _create_record(
            whose,
            when=None,
            meal_params_list=(),
            metering_params=None,
            injection_params_list=(),
            comments_params_list=(),
    ):

        if when is None:
            when = create_datetime('2021-05-10T13:15:00')

        record = Record.objects.create(
            who=whose,
            when=when,
        )

        if metering_params is not None:
            metering_params['record'] = record
            create_sugar_metering(
                **metering_params,
            )

        for params in meal_params_list:
            params['record'] = record
            create_meal(**params)

        for params in injection_params_list:
            params['record'] = record
            create_insulin_injection(**params)

        for params in comments_params_list:
            params['record'] = record
            create_comment(**params)

        return record

    return _create_record


@pytest.fixture
def db_data_base_dir(request, resources):
    """
    Base directory for db data
    """
    _db_data_base_dir = pathlib.Path(resources) / 'sugar' / 'db_data'
    try:
        _db_data_base_dir /= request.param
    except AttributeError:
        pass

    return _db_data_base_dir


@pytest.fixture
def db_data(
        request,
        transactional_db,

        create_record,
        create_user,

        db_data_base_dir,
):
    file_path = db_data_base_dir / request.param

    with open(file_path, 'rt', encoding='utf-8') as f:
        db_data_params = yaml.load(f, Loader=yaml.FullLoader)

    _db_data = {}

    default_user = None
    _db_data['users'] = users = {}
    users_params = db_data_params.get('users') or {}
    for username, kwargs in users_params.items():
        is_default = kwargs.pop('default', False)
        users[username] = user = create_user(username, **kwargs)
        if is_default:
            if default_user is not None:
                logger.error('Multiple default users!')
            default_user = user

    _db_data['records'] = records = []
    records_params = db_data_params.get('records') or []
    for record_params in records_params:
        try:
            username = record_params['whose']
        except KeyError:
            record_params['whose'] = default_user
        else:
            record_params['whose'] = users[username]

        record = create_record(**record_params)
        records.append(record)

    return _db_data
