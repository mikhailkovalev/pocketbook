import json
import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import ANY  # fixme: need?

import pytest
import pytz
from django.conf import settings


@pytest.fixture
def override_settings(settings):
    settings.DEFAULT_PAGE_SIZE = 3


@pytest.fixture
def json_file_name() -> str:
    return 'this-file-does-not-exist.json'


@pytest.fixture
def json_file(
        resources,
        json_file_name,
) -> str:
    return os.path.abspath(os.path.join(
        resources,
        json_file_name,
    ))


@pytest.fixture
def no_groupping_records(
        resources,
):
    pass


def test_no_groupping(
        override_settings,

        create_client,
        create_record,

        admin,
):
    # todo: записи других пользователей не отображаются
    # todo: постраничное отображение (на нужной странице -- нужные записи)
    # todo: если данных нет -- стоит прочерк
    tz = pytz.timezone(settings.TIME_ZONE)

    create_record(
        whose=admin,
        when=tz.localize(datetime(2022, 2, 6, 3)),
        metering_params={
            'sugar_level': Decimal('8.0'),
        },
    )
    create_record(
        whose=admin,
        when=tz.localize(datetime(2022, 2, 6, 8)),
        metering_params={
            'sugar_level': Decimal('6.0'),
        },
    )
    create_record(
        whose=admin,
        when=tz.localize(datetime(2022, 2, 6, 12, 30)),
        metering_params=None,
    )
    create_record(
        whose=admin,
        when=tz.localize(datetime(2022, 2, 6, 15, 30)),
        metering_params={
            'sugar_level': Decimal('10.0'),
        },
    )
    create_record(
        whose=admin,
        when=tz.localize(datetime(2022, 2, 6, 22)),
        metering_params={
            'sugar_level': Decimal('4.0'),
        },
    )

    client = create_client(authenticated_with=admin)
    response = client.post(
        '/sugar/rows.json',
        data={
            'page_number': 1,
            'groupping': 'none',
        },
    )

    assert response.status_code == 200

    parsed_response = json.loads(response.content.decode('utf-8'))
    assert parsed_response == {
        'rows': [
            {
                'time_label': '2022-02-06 22:00',
                'sugar_level': '4.0',
                'meal': None,
            },
            {
                'time_label': '2022-02-06 15:30',
                'sugar_level': '10.0',
                'meal': None,
            },
            {
                'time_label': '2022-02-06 12:30',
                'sugar_level': None,
                'meal': None,
            },
        ],
        'columns': [
            {
                'data_index': 'time_label',
                'header': 'Дата/время',
            },
            {
                'data_index': 'sugar_level',
                'header': 'Сахар крови',
            },
            {
                'data_index': 'meal',
                'header': 'Съедено (ХЕ)',
            },
        ],
        'total_rows_count': 5,
        'total_pages_count': 2,
        'page_number': 1,
        'first_shown': 1,
        'last_shown': 3,
    }


def test_days(
        override_settings,
):
    pass


def test_weeks(
        override_settings,
):
    pass


def test_months(
        override_settings,
):
    pass


def test_years(
        override_settings,
):
    pass
