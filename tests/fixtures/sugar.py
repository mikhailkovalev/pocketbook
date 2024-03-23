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
            id=None,
    ):

        if when is None:
            when = create_datetime('2021-05-10T13:15:00')

        record = Record.objects.create(
            **({'id': id} if id is not None else {}),
            who=whose,
            when=when,  # todo: wrap to create_datetime?
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
