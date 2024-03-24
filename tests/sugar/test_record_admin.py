import pathlib
from datetime import (
    date,
    datetime,
)
from decimal import (
    Decimal,
)

import pytest
from django.contrib.auth.models import User
from django.db.utils import (
    IntegrityError,
)
from lxml import (
    etree,
)

from sugar import models


def test_add_record(
        create_client,
        db_data_base_dir,
        admin,
):
    url = '/admin/sugar/record/add/'
    client = create_client(
        authenticated_with=admin,
    )
    response = client.get(url)

    assert response.status_code == 200

    etree_html_parser = etree.HTMLParser()
    tree = etree.XML(
        text=response.content.decode('utf=8'),
        parser=etree_html_parser,
    )

    date_value = tree.xpath(
        '//div[@class="form-row field-when"]'
        '/div'
        '/p[@class="datetime"]'
        '/input[@name="when_0"]'
        '/@value'
    )
    assert date_value == []

    time_value = tree.xpath(
        '//div[@class="form-row field-when"]'
        '/div'
        '/p[@class="datetime"]'
        '/input[@name="when_1"]'
        '/@value'
    )
    assert time_value == []

    selected_metering_pack = tree.xpath(
        '//div[@id="sugarmetering-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "sugarmetering-")]'
        '/td[@class="field-pack"]'
        '/div'
        '/select[@id="id_sugarmetering-0-pack"]'
        '/option[@selected]'
        '/text()'
    )
    assert selected_metering_pack == [
        '---------',
    ]

    sugar_level = tree.xpath(
        '//div[@id="sugarmetering-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "sugarmetering-")]'
        '/td[@class="field-sugar_level"]'
        '/input[@id="id_sugarmetering-0-sugar_level"]'
        '/@value'
    )
    assert sugar_level == []

    food_quantity = tree.xpath(
        '//div[@id="meal_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "meal_set")]'
        '/td[@class="field-food_quantity"]'
        '/input'
        '/@value'
    )
    assert food_quantity == []

    food_description = tree.xpath(
        '//div[@id="meal_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "meal_set-")]'
        '/td[@class="field-description"]'
        '/input'
        '/@value'
    )
    assert food_description == []

    selected_syringe = tree.xpath(
        '//div[@id="insulininjection_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[@id="insulininjection_set-0"]'
        '/td[@class="field-insulin_syringe"]'
        '/div'
        '/select'
        '/option[@selected]'
        '/text()'
    )
    assert selected_syringe == [
        '---------',
    ]

    insulin_quantity = tree.xpath(
        '//div[@id="insulininjection_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "insulininjection_set-")]'
        '/td[@class="field-insulin_quantity"]'
        '/input'
        '/@value'
    )
    assert insulin_quantity == []

    comment = tree.xpath(
        '//div[@id="comment_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[@id="comment_set-0"]'
        '/td[@class="field-content"]'
        '/textarea'
        '/text()'
    )
    assert tuple(map(str.strip, comment)) == (
        '',
    )


@pytest.mark.parametrize('db_data_filename', ['test_records_list_ownership.yml'])
@pytest.mark.parametrize('db_data_base_dir', [pathlib.Path('sugar', 'db_data', 'test_record_admin')])  # todo: use pytestmark?
@pytest.mark.parametrize(
    ['username', 'expected_records_markers'],
    [
        [
            'admin',
            [
                '2021-05-16 10:00',
                '2021-05-16 11:00',
                '2021-05-16 12:00',
            ],
        ],
        [
            'admin2',
            [
                '2021-05-16 10:30',
                '2021-05-16 11:30',
            ],
        ],
    ],
)
def test_records_list_ownership(
        create_client,
        db_data,
        username,
        expected_records_markers,
):
    user = User.objects.get(username=username)

    etree_html_parser = etree.HTMLParser()  # fixme: fixture?
    search_equation = '//table[@id="result_list"]/tbody/tr/th/a/text()'

    client = create_client(
        authenticated_with=user,
    )
    response = client.get('/admin/sugar/record/')
    assert response.status_code == 200

    tree = etree.XML(
        text=response.content,
        parser=etree_html_parser,
    )
    markers = tree.xpath(search_equation)
    markers.sort()
    assert markers == expected_records_markers


@pytest.mark.parametrize(
    [
        'db_data_filename',
        'expected_meterings_data',
        'expected_meal_data',
        'expected_injections_data',
        'expected_comments_data',
    ],
    [
        [
            'test_records_list_display_basic.yml',
            ['4.8', '-'],  # expected_meterings_data
            ['2.0', '-'],  # expected_meal_data
            ['4 Aspart', '-'],  # expected_injections_data
            ['Foo', '-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_multiple_meals.yml',
            ['-'],  # expected_meterings_data
            ['4.0'],  # expected_meal_data
            ['-'],  # expected_injections_data
            ['-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_multiple_injections.yml',
            ['-'],  # expected_meterings_data
            ['-'],  # expected_meal_data
            ['4+4 Foo, 10 Bar'],  # expected_injections_data
            ['-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_multiple_comments.yml',
            ['-'],  # expected_meterings_data
            ['-'],  # expected_meal_data
            ['-'],  # expected_injections_data
            ['Foo; Bar'],  # expected_comments_data
        ],
        [
            'test_records_list_display_long_comment.yml',
            ['-'],  # expected_meterings_data
            ['-'],  # expected_meal_data
            ['-'],  # expected_injections_data
            ['Just an incredi<...>'],  # expected_comments_data
        ],
    ],
)
@pytest.mark.parametrize('db_data_base_dir', [pathlib.Path('sugar', 'db_data', 'test_record_admin')])  # todo: use pytestmark?
def test_records_list_display(
        create_client,
        db_data,
        expected_meterings_data,
        expected_meal_data,
        expected_injections_data,
        expected_comments_data,
):
    admin = User.objects.get(username='admin')

    client = create_client(
        authenticated_with=admin,
    )
    response = client.get('/admin/sugar/record/')
    assert response.status_code == 200

    etree_html_parser = etree.HTMLParser()
    tree = etree.XML(
        text=response.content,
        parser=etree_html_parser,
    )

    search_template = '//table[@id="result_list"]/tbody/tr/td[@class="{}"]/text()'  # noqa

    meterings_search = search_template.format('field-sugar_level')
    meal_search = search_template.format('field-total_meal')
    injections_search = search_template.format('field-injections_info')
    comments_search = search_template.format('field-short_comments')

    assert tree.xpath(meterings_search) == expected_meterings_data 
    assert tree.xpath(meal_search) == expected_meal_data 
    assert tree.xpath(injections_search) == expected_injections_data 
    assert tree.xpath(comments_search) == expected_comments_data 


@pytest.mark.parametrize(
    [
        'db_data_filename',
        'expected_date_data',
        'expected_time_data',
        'expected_pack_data',
        'expected_pack_options',
        'expected_meterings_data',
        'expected_meal_data',
        'expected_meal_description_data',
        'expected_syringes_data',
        'expected_syringes_options',
        'expected_injections_data',
        'expected_comments_data',
    ],
    [
        [
            'test_change_display_basic.yml',  # db_data_filename
            ['2021-05-16'],  # expected_date_data
            ['11:00:00'],  # expected_time_data
            ['Пачка тест-полосок от 2021-05-05', '---------'],  # expected_pack_data
            ['---------', 'Пачка тест-полосок от 2021-05-05', 'Пачка тест-полосок от 2021-05-06'] * 2,  # expected_pack_options
            ['4.8'],  # expected_meterings_data
            ['2.0'],  # expected_meal_data
            ['Foo'],  # expected_meal_description_data
            # region expected_syringes_data
            [
                'Шприц "Aspart" (300 ед.) от 2021-05-07',
                '---------',
                '---------',
            ],
            # endregion
            ['---------', 'Шприц "Aspart" (300 ед.) от 2021-05-07'] * 3,  # expected_syringes_options
            ['4'],  # expected_injections_data
            ['Bar', '', ''],  # expected_comments_data
        ],
        [
            'test_change_display_multiple_meals.yml',  # db_data_filename
            ['2021-05-16'],  # expected_date_data
            ['11:00:00'],  # expected_time_data
            ['---------', '---------'],  # expected_pack_data
            ['---------'] * 2,  # expected_pack_options
            [],  # expected_meterings_data
            ['2.0', '3.0'],  # expected_meal_data
            ['Foo', 'Bar'],  # expected_meal_description_data
            ['---------', '---------'],  # expected_syringes_data
            ['---------', '---------'],  # expected_syringes_options
            [],  # expected_injections_data
            ['', ''],  # expected_comments_data
        ],
        [
            'test_change_display_multiple_injections.yml',  # db_data_filename
            ['2021-05-16'],  # expected_date_data
            ['11:00:00'],  # expected_time_data
            ['---------', '---------'],  # expected_pack_data
            ['---------'] * 2,  # expected_pack_options
            [],  # expected_meterings_data
            [],  # expected_meal_data
            [],  # expected_meal_description_data
            # region expected_syringes_data
            [
                'Шприц "Foo" (300 ед.) от 2021-05-01',
                'Шприц "Foo" (300 ед.) от 2021-05-01',
                'Шприц "Bar" (300 ед.) от 2021-05-02',
                '---------',
                '---------',
            ],
            # endregion
            ['---------', 'Шприц "Foo" (300 ед.) от 2021-05-01', 'Шприц "Bar" (300 ед.) от 2021-05-02'] * 5,  # expected_syringes_options
            ['4', '4', '10'],  # expected_injections_data
            ['', ''],  # expected_comments_data
        ],
        [
            'test_change_display_multiple_comments.yml',  # db_data_filename
            ['2021-05-16'],  # expected_date_data
            ['11:00:00'],  # expected_time_data
            ['---------', '---------'],  # expected_pack_data
            ['---------'] * 2,  # expected_pack_options
            [],  # expected_meterings_data
            [],  # expected_meal_data
            [],  # expected_meal_description_data
            ['---------', '---------'],  # expected_syringes_data
            ['---------', '---------'],  # expected_syringes_options
            [],  # expected_injections_data
            ['Foo', 'Bar', '', ''],  # expected_comments_data
        ],
    ],
)
@pytest.mark.parametrize('db_data_base_dir', [pathlib.Path('sugar', 'db_data', 'test_record_admin')])  # todo: use pytestmark?
def test_change_display(
        create_client,
        db_data,
        expected_date_data,
        expected_time_data,
        expected_pack_data,
        expected_pack_options,
        expected_meterings_data,
        expected_meal_data,
        expected_meal_description_data,
        expected_syringes_data,
        expected_syringes_options,
        expected_injections_data,
        expected_comments_data,
):
    admin = User.objects.get(username='admin')
    record = models.Record.objects.get()
    client = create_client(
        authenticated_with=admin,
    )
    response = client.get(f'/admin/sugar/record/{record.pk}/change/')
    assert response.status_code == 200

    etree_html_parser = etree.HTMLParser()
    tree = etree.XML(
        text=response.content.decode('utf=8'),
        parser=etree_html_parser,
    )

    date_value = tree.xpath(
        '//div[@class="form-row field-when"]'
        '/div'
        '/p[@class="datetime"]'
        '/input[@name="when_0"]'
        '/@value'
    )
    assert date_value == expected_date_data

    time_value = tree.xpath(
        '//div[@class="form-row field-when"]'
        '/div'
        '/p[@class="datetime"]'
        '/input[@name="when_1"]'
        '/@value'
    )
    assert time_value == expected_time_data

    selected_metering_pack = tree.xpath(
        '//div[@id="sugarmetering-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "sugarmetering-")]'
        '/td[@class="field-pack"]'
        '/div'
        '/select['
        '    starts-with(@id, "id_sugarmetering-")'
        '    and contains(@id, "pack")'
        '    and substring-after(@id, "pack") = ""'
        ']'
        '/option[@selected]'
        '/text()'
    )
    assert selected_metering_pack == expected_pack_data
    
    pack_options = tree.xpath(
        '//div[@id="sugarmetering-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "sugarmetering-")]'
        '/td[@class="field-pack"]'
        '/div'
        '/select['
        '    starts-with(@id, "id_sugarmetering-")'
        '    and contains(@id, "pack")'
        '    and substring-after(@id, "pack") = ""'
        ']'
        '/option'
        '/text()'
    )
    assert pack_options == expected_pack_options

    sugar_level = tree.xpath(
        '//div[@id="sugarmetering-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "sugarmetering-")]'
        '/td[@class="field-sugar_level"]'
        '/input['
        '    starts-with(@id, "id_sugarmetering-")'
        '    and contains(@id, "-sugar_level")'
        '    and substring-after(@id, "-sugar_level") = ""'
        ']'
        '/@value'
    )
    assert sugar_level == expected_meterings_data

    food_quantity = tree.xpath(
        '//div[@id="meal_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "meal_set-")]'
        '/td[@class="field-food_quantity"]'
        '/input'
        '/@value'
    )
    assert food_quantity == expected_meal_data

    food_description = tree.xpath(
        '//div[@id="meal_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "meal_set-")]'
        '/td[@class="field-description"]'
        '/input'
        '/@value'
    )
    assert food_description == expected_meal_description_data

    selected_syringe = tree.xpath(
        '//div[@id="insulininjection_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "insulininjection_set-")]'
        '/td[@class="field-insulin_syringe"]'
        '/div'
        '/select['
        '    starts-with(@id, "id_insulininjection_set-")'
        '    and contains(@id, "-insulin_syringe")'
        '    and substring-after(@id, "-insulin_syringe") = ""'
        ']'
        '/option[@selected]'
        '/text()'
    )
    assert selected_syringe == expected_syringes_data

    syringe_options = tree.xpath(
        '//div[@id="insulininjection_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "insulininjection_set-")]'
        '/td[@class="field-insulin_syringe"]'
        '/div'
        '/select['
        '    starts-with(@id, "id_insulininjection_set-")'
        '    and contains(@id, "-insulin_syringe")'
        '    and substring-after(@id, "-insulin_syringe") = ""'
        ']'
        '/option'
        '/text()'
    )
    assert syringe_options == expected_syringes_options

    insulin_quantity = tree.xpath(
        '//div[@id="insulininjection_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "insulininjection_set-")]'
        '/td[@class="field-insulin_quantity"]'
        '/input'
        '/@value'
    )
    assert insulin_quantity == expected_injections_data

    comment = tree.xpath(
        '//div[@id="comment_set-group"]'
        '/div'
        '/fieldset'
        '/table'
        '/tbody'
        '/tr[starts-with(@id, "comment_set-")]'
        '/td[@class="field-content"]'
        '/textarea'
        '/text()'
    )
    assert list(map(str.strip, comment)) == expected_comments_data

# todo: move
# def test_multiple_meterings(
#         create_datetime,
#         create_record,
#         create_sugar_metering,
#         db_data_base_dir,
# ):
#     record = create_record()
#     create_sugar_metering(
#         record=record,
#         sugar_level=Decimal('4.8'),
#     )
#
#     with pytest.raises(IntegrityError):
#         create_sugar_metering(
#             record=record,
#             sugar_level=Decimal('6.8'),
#         )


def test_actuality_for_new(
        create_client,
        create_insulin_syringe,
        create_test_strip_pack,
        admin,
        tz,
        db_data_base_dir,
):
    create_test_strip_pack(  # expired pack
        whose=admin,
        volume=50,
        opening=date(
            year=2021,
            month=4,
            day=1,
        ),
        expiry_plan=date(
            year=2021,
            month=5,
            day=1,
        ),
        expiry_actual=date(
            year=2021,
            month=4,
            day=30,
        ),
    )
    create_test_strip_pack(  # actual pack
        whose=admin,
        volume=50,
        opening=date(
            year=2021,
            month=5,
            day=1,
        ),
        expiry_plan=date(
            year=2021,
            month=6,
            day=1,
        ),
    )

    today = tz.localize(datetime.now()).date()
    create_test_strip_pack(  # actual pack
        whose=admin,
        volume=50,
        opening=date(
            year=2021,
            month=5,
            day=10,
        ),
        expiry_plan=date(
            year=2021,
            month=6,
            day=10,
        ),
        expiry_actual=today,
    )
    create_insulin_syringe(  # expired syringe
        whose=admin,
        volume=300,
        opening=date(
            year=2021,
            month=4,
            day=1,
        ),
        expiry_plan=date(
            year=2021,
            month=5,
            day=1,
        ),
        expiry_actual=date(
            year=2021,
            month=4,
            day=30,
        ),
    )
    create_insulin_syringe(  # actual syringe
        whose=admin,
        volume=300,
        opening=date(
            year=2021,
            month=5,
            day=1,
        ),
        expiry_plan=date(
            year=2021,
            month=6,
            day=1,
        ),
    )
    create_insulin_syringe(  # actual syringe
        whose=admin,
        volume=300,
        opening=date(
            year=2021,
            month=5,
            day=10,
        ),
        expiry_plan=date(
            year=2021,
            month=6,
            day=1,
        ),
        expiry_date=today,
    )

    client = create_client(
        authenticated_with=admin,
    )

    response = client.get('/admin/sugar/record/add/')
    assert response.status_code == 200
    
    etree_html_parser = etree.HTMLParser()
    tree = etree.XML(
        text=response.content.decode('utf-8'),
        parser=etree_html_parser,
    )

    select_pack_search = '//select[@name="sugarmetering-0-pack"]/option/text()'
    assert tree.xpath(select_pack_search)[1:] == [
        'Пачка тест-полосок от 2021-05-01',
        'Пачка тест-полосок от 2021-05-10',
    ]

    select_syringe_search = '//select[@name="insulininjection_set-0-insulin_syringe"]/option/text()'  # noqa
    assert tree.xpath(select_syringe_search)[1:] == [
        'Шприц "Aspart" (300 ед.) от 2021-05-01',
        'Шприц "Aspart" (300 ед.) от 2021-05-10',
    ]
