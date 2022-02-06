import os.path
from datetime import (
    date,
)
from decimal import (
    Decimal,
)
from unittest.mock import (
    ANY,
)

import pytest
from django.core.management import call_command

from sugar.models import (
    Record,
    SugarMetering,
)


@pytest.fixture
def csv_file_name() -> str:
    return 'import-sugar-csv-correct.csv'


@pytest.fixture
def csv_file(
        csv_file_name,
        resources,
) -> str:
    return os.path.abspath(os.path.join(
        resources,
        csv_file_name,
    ))


@pytest.fixture
def pack(
        admin,
        create_test_strip_pack,
):
    return create_test_strip_pack(
        whose=admin,
        volume=50,
        opening=date(2021, 9, 10),
        expiry_plan=date(2021, 9, 20),
    )


@pytest.fixture
def expired_pack(
        admin,
        create_test_strip_pack,
):
    return create_test_strip_pack(
        whose=admin,
        volume=50,
        opening=date(2021, 9, 5),
        expiry_plan=date(2021, 9, 15),
        expiry_actual=date(2021, 9, 14)
    )


@pytest.mark.parametrize('expired_pack_', (
    None,
    pytest.lazy_fixture('expired_pack'),  # noqa
))
def test_success(
        admin,
        create_datetime,
        create_test_strip_pack,
        csv_file,
        expired_pack_,
        model_to_dict,
        pack,
):
    call_command(
        'import-sugar-csv',
        username=admin.username,
        csv_file_path=csv_file,
    )

    records = tuple(map(
        model_to_dict,
        Record.objects.order_by('-when'),
    ))
    assert records == (
        {
            'id': ANY,
            'who_id': admin.pk,
            'when': create_datetime('2021-09-15T23:03:00'),
        },
        {
            'id': ANY,
            'who_id': admin.pk,
            'when': create_datetime('2021-09-15T03:03:00'),
        },
    )

    meterings = tuple(map(
        model_to_dict,
        SugarMetering.objects.order_by('-record__when'),
    ))
    assert meterings == (
        {
            'id': ANY,
            'record_id': ANY,
            'pack_id': pack.pk,
            'sugar_level': Decimal('4.7'),
        },
        {
            'id': ANY,
            'record_id': ANY,
            'pack_id': pack.pk,
            'sugar_level': Decimal('5.0'),
        },
    )


def test_fail_if_there_is_no_such_user(
        admin,
        csv_file,
):
    with pytest.raises(ValueError) as exc_info:
        call_command(
            'import-sugar-csv',
            username='odmen',  # there's no such user
            csv_file_path=csv_file,
        )

    assert str(exc_info.value) == "There is no user 'odmen'"
    assert tuple(Record.objects.all()) == ()
    assert tuple(SugarMetering.objects.all()) == ()


@pytest.mark.parametrize('expired_pack_', (
    None,
    pytest.lazy_fixture('expired_pack'),  # noqa
))
def test_fail_if_there_is_no_pack(
        admin,
        csv_file,
        expired_pack_,
):
    with pytest.raises(ValueError) as exc_info:
        call_command(
            'import-sugar-csv',
            username=admin.username,
            csv_file_path=csv_file,
        )

    assert str(exc_info.value) == 'There is no "TestStripPack" object which is not expired!'  # noqa
    assert tuple(Record.objects.all()) == ()
    assert tuple(SugarMetering.objects.all()) == ()


@pytest.mark.parametrize('expired_pack_', (
    None,
    pytest.lazy_fixture('expired_pack'),  # noqa
))
def test_fail_if_many_packs(
        admin,
        create_test_strip_pack,
        csv_file,
        expired_pack_,
        pack,
):
    create_test_strip_pack(
        whose=admin,
        volume=50,
        opening=date(2021, 9, 11),
        expiry_plan=date(2021, 9, 21),
    )

    with pytest.raises(ValueError) as exc_info:
        call_command(
            'import-sugar-csv',
            username=admin.username,
            csv_file_path=csv_file,
        )

    assert str(exc_info.value) == 'There are many "TestStripPack" objects which are not expired!'  # noqa
    assert tuple(Record.objects.all()) == ()
    assert tuple(SugarMetering.objects.all()) == ()


@pytest.mark.parametrize(
    (
        'csv_file_name',
        'expected_error',
    ),
    (
        (
            'import-sugar-csv-wrong-date.csv',
            "Incorrect date value '20210915' in line 2",
        ),
        (
            'import-sugar-csv-wrong-time.csv',
            "Incorrect time value '3-3' in line 2",
        ),
        (
            'import-sugar-csv-wrong-sugar-level.csv',
            "Incorrect sugar_level value '5.55' in line 2",
        ),
    ),
)
def test_wrong_data(
        admin,
        csv_file,
        csv_file_name,
        expected_error,
        pack,
):
    with pytest.raises(ValueError) as exc_info:
        call_command(
            'import-sugar-csv',
            username=admin.username,
            csv_file_path=csv_file,
        )

    assert str(exc_info.value) == expected_error
    assert tuple(Record.objects.all()) == ()
    assert tuple(SugarMetering.objects.all()) == ()
