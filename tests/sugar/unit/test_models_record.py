import datetime as dt
from decimal import Decimal

import pytest
import pytz
from django.conf import settings


@pytest.mark.parametrize(
    [
        'metering_params',
        'expected_sugar_level',
    ],
    [
        [
            None,
            None,
        ],
        [
            {'sugar_level': '4.8'},
            Decimal('4.8'),
        ],
    ],
)
def test_cache_sugar_level(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        metering_params,
        expected_sugar_level,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        metering_params=metering_params,
    )
    # endregion

    # region act
    result = record.sugar_level()
    # endregion

    # region assert
    assert result == expected_sugar_level
    assert record._sugar_level == expected_sugar_level
    # endregion


@pytest.mark.parametrize(
    'metering_params',
    [
        None,
        {'sugar_level': '4.8'},
    ],
)
def test_use_cached_sugar_level(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        metering_params,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        metering_params=metering_params,
    )
    record._sugar_level = Decimal('5.0')
    # endregion

    # region act
    result = record.sugar_level()
    # endregion

    # region assert
    assert result == Decimal('5.0')
    assert record._sugar_level == Decimal('5.0')
    # endregion


@pytest.mark.parametrize(
    [
        'meal_params_list',
        'expected_total_meal',
    ],
    [
        [
            (),
            None,
        ],
        [
            ({'food_quantity': '1.0'}, {'food_quantity': '1.5'}),
            Decimal('2.5'),
        ],
    ],
)
def test_cache_total_meal(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        meal_params_list,
        expected_total_meal,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        meal_params_list=meal_params_list,
    )
    # endregion

    # region act
    result = record.total_meal()
    # endregion

    # region assert
    assert result == expected_total_meal
    assert record._total_meal == expected_total_meal
    # endregion


@pytest.mark.parametrize(
    'meal_params_list',
    [
        (),
        ({'food_quantity': '1.0'}, {'food_quantity': '1.5'}),
    ],
)
def test_use_cached_total_meal(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        meal_params_list,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        meal_params_list=meal_params_list,
    )
    record._total_meal = Decimal('5.0')
    # endregion

    # region act
    result = record.total_meal()
    # endregion

    # region assert
    assert result == Decimal('5.0')
    assert record._total_meal == Decimal('5.0')
    # endregion


@pytest.mark.parametrize(
    [
        'injection_params_list',
        'expected_injections_info',
    ],
    [
        [
            (),
            None,
        ],
        [
            ({'insulin_quantity': 1}, {'insulin_quantity': 2}),
            '1+2 Aspart',
        ],
    ],
)
def test_cache_injections_info(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        injection_params_list,
        expected_injections_info,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        injection_params_list=injection_params_list,
    )
    # endregion

    # region act
    result = record.injections_info()
    # endregion

    # region assert
    assert result == expected_injections_info
    assert record._injections_info == expected_injections_info
    # endregion


@pytest.mark.parametrize(
    'injection_params_list',
    [
        (),
        ({'insulin_quantity': 1}, {'insulin_quantity': 2}),
    ],
)
def test_use_cached_injections_info(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        injection_params_list,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        injection_params_list=injection_params_list,
    )
    record._injections_info = 'foo'
    # endregion

    # region act
    result = record.injections_info()
    # endregion

    # region assert
    assert result == 'foo'
    assert record._injections_info == 'foo'
    # endregion


@pytest.mark.parametrize(
    [
        'comments_params_list',
        'expected_short_comments',
    ],
    [
        [
            (),
            None,
        ],
        [
            ({'content': 'foo'}, {'content': 'bar'}),
            'foo; bar',
        ],
    ],
)
def test_cache_short_comments(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        comments_params_list,
        expected_short_comments,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        comments_params_list=comments_params_list,
    )
    # endregion

    # region act
    result = record.short_comments()
    # endregion

    # region assert
    assert result == expected_short_comments
    assert record._short_comments == expected_short_comments
    # endregion


@pytest.mark.parametrize(
    'comments_params_list',
    [
        (),
        ({'content': 'foo'}, {'content': 'bar'}),
    ],
)
def test_use_cached_short_comments(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion

        # region params
        comments_params_list,
        # endregion
):
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
        comments_params_list=comments_params_list,
    )
    record._short_comments = 'buz'
    # endregion

    # region act
    result = record.short_comments()
    # endregion

    # region assert
    assert result == 'buz'
    assert record._short_comments == 'buz'
    # endregion


def test_cache_is_cleared(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion
):
    """
    Кэш очищается, если вызываем `refresh_from_db`
    с пустым параметром `fields`
    """
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
    )
    record._sugar_level = Decimal('5.0')
    record._total_meal = Decimal('2.0')
    record._injections_info = 'foo'
    record._short_comments = 'bar'
    # endregion

    # region act
    record.refresh_from_db()
    # endregion

    # region assert
    assert not hasattr(record, '_sugar_level')
    assert not hasattr(record, '_total_meal')
    assert not hasattr(record, '_injections_info')
    assert not hasattr(record, '_short_comments')
    # endregion


def test_cache_is_not_cleared(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion
):
    """
    Кэш не очищается, если вызываем `refresh_from_db`
    с непустым параметром `fields`
    """
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
    )
    record._sugar_level = Decimal('5.0')
    record._total_meal = Decimal('2.0')
    record._injections_info = 'foo'
    record._short_comments = 'bar'
    # endregion

    # region act
    record.refresh_from_db(fields=['who', 'when'])
    # endregion

    # region assert
    assert record._sugar_level == Decimal('5.0')
    assert record._total_meal == Decimal('2.0')
    assert record._injections_info == 'foo'
    assert record._short_comments == 'bar'
    # endregion


def test_clear_empty_cache(
        # region fabrics
        create_record,
        # endregion

        # region fixtures
        admin,
        # endregion
):
    """
    Не падаем, если пытаемся очистить кэш, который не был заполнен
    """
    # region setup
    tz = pytz.timezone(settings.TIME_ZONE)

    record = create_record(
        whose=admin,
        when=tz.localize(dt.datetime(
            year=2021,
            month=5,
            day=16,
            hour=10,
            minute=0,
        )),
    )
    assert not hasattr(record, '_sugar_metering')
    assert not hasattr(record, '_total_meal')
    assert not hasattr(record, '_injections_info')
    assert not hasattr(record, '_short_comments')
    # endregion

    # region act
    record.refresh_from_db()
    # endregion

    # region assert
    assert not hasattr(record, '_sugar_level')
    assert not hasattr(record, '_total_meal')
    assert not hasattr(record, '_injections_info')
    assert not hasattr(record, '_short_comments')
    # endregion
