import json
import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import ANY  # fixme: need?

import pytest
import pytz
from django.conf import settings


pytestmark = [
    pytest.mark.parametrize('default_page_size', (3,)),
]


@pytest.fixture
def records(
        create_record,
        create_user,

        admin,
):
    admin2 = create_user(
        username='admin2',
        is_staff=True,
        is_superuser=True,
    )

    return (
        # region admin2
        create_record(
            whose=admin2,
            when=datetime.fromisoformat('2022-02-06T11:00:00.000+03:00'),
            metering_params={
                'sugar_level': Decimal('6.0'),
            },
        ),
        create_record(
            whose=admin2,
            when=datetime.fromisoformat('2022-02-06T23:00:00.000+03:00'),
            metering_params={
                'sugar_level': Decimal('4.0'),
            },
        ),
        # endregion
        # region 2022-02-10
        # todo
        # endregion
        # region 2022-02-09
        # todo
        # endregion
        # region 2022-02-07
        # todo
        # endregion
        # region 2022-02-06
        create_record(
            whose=admin,
            when=datetime.fromisoformat('2022-02-06T03:00:00.000+03:00'),            metering_params={
                'sugar_level': Decimal('8.0'),
            },
        ),
        create_record(
            whose=admin,
            when=datetime.fromisoformat('2022-02-06T08:00:00.000+03:00'),
            metering_params={
                'sugar_level': Decimal('6.0'),
            },
        ),
        create_record(
            whose=admin,
            when=datetime.fromisoformat('2022-02-06T12:30:00.000+03:00'),
            metering_params=None,
        ),
        create_record(
            whose=admin,
            when=datetime.fromisoformat('2022-02-06T15:30:00.000+03:00'),
            metering_params={
                'sugar_level': Decimal('10.0'),
            },
        ),
        create_record(
            whose=admin,
            when=datetime.fromisoformat('2022-02-06T22:00:00.000+03:00'),
            metering_params={
                'sugar_level': Decimal('4.0'),
            },
        ),
        # endregion
    )


@pytest.mark.parametrize(
    (
        'expected_response',
        'groupping',
        'page_number',
    ),
    (
        (
            {   # expected_response
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
            },
            'none',  # groupping
            1,  # page_number
        ),
        (
            {   # expected_response
                'rows': [
                    {
                        'time_label': '2022-02-06 08:00',
                        'sugar_level': '6.0',
                        'meal': None,
                    },
                    {
                        'time_label': '2022-02-06 03:00',
                        'sugar_level': '8.0',
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
                'page_number': 2,
                'first_shown': 4,
                'last_shown': 5,
            },
            'none',  # groupping
            2,  # page_number
        ),
    ),
)
def test_no_groupping(
        create_client,
        create_record,

        admin,
        expected_response,
        groupping,
        page_number,
        records,
):
    # todo: записи других пользователей не отображаются
    # todo: постраничное отображение (на нужной странице -- нужные записи)
    # todo: если данных нет -- стоит прочерк
    client = create_client(authenticated_with=admin)
    response = client.post(
        '/sugar/rows.json',
        data={
            'page_number': page_number,
            'groupping': groupping,
        },
    )

    assert response.status_code == 200

    parsed_response = json.loads(response.content.decode('utf-8'))
    assert parsed_response == expected_response

# def test_days(
#         override_settings,
# ):
#     pass
#
#
# def test_weeks(
#         override_settings,
# ):
#     pass
#
#
# def test_months(
#         override_settings,
# ):
#     pass
#
#
# def test_years(
#         override_settings,
# ):
#     pass
