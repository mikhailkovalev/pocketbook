import pathlib

import pytest
from django.contrib.auth.models import User
from lxml import (
    etree,
)

from sugar import models

pytestmark = [
    pytest.mark.parametrize('db_data_base_dir', [pathlib.Path('sugar', 'db_data', 'test_record_admin')]),
]


@pytest.mark.parametrize(
    [
        'db_data_filename',
        'username',
        'expected_when_data',
        'expected_meterings_data',
        'expected_meal_data',
        'expected_injections_data',
        'expected_comments_data',
    ],
    [
        [
            'test_records_list_display_basic.yml',
            'admin',  # username
            ['2021-05-16 11:00', '2021-05-16 10:00'],  # expected_when_data
            ['4.8', '-'],  # expected_meterings_data
            ['2.0', '-'],  # expected_meal_data
            ['4 Aspart', '-'],  # expected_injections_data
            ['Foo', '-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_ownership.yml',
            'admin',  # username
            ['2021-05-16 12:00', '2021-05-16 11:00', '2021-05-16 10:00'],  # expected_when_data
            ['-', '-', '-'],  # expected_meterings_data
            ['-', '-', '-'],  # expected_meal_data
            ['-', '-', '-'],  # expected_injections_data
            ['-', '-', '-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_ownership.yml',
            'admin2',  # username
            ['2021-05-16 11:30', '2021-05-16 10:30'],  # expected_when_data
            ['-', '-'],  # expected_meterings_data
            ['-', '-'],  # expected_meal_data
            ['-', '-'],  # expected_injections_data
            ['-', '-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_multiple_meals.yml',
            'admin',  # username
            ['2021-05-16 11:00'],  # expected_when_data
            ['-'],  # expected_meterings_data
            ['4.0'],  # expected_meal_data
            ['-'],  # expected_injections_data
            ['-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_multiple_injections.yml',
            'admin',  # username
            ['2021-05-16 11:00'],  # expected_when_data
            ['-'],  # expected_meterings_data
            ['-'],  # expected_meal_data
            ['4+4 Foo, 10 Bar'],  # expected_injections_data
            ['-'],  # expected_comments_data
        ],
        [
            'test_records_list_display_multiple_comments.yml',
            'admin',  # username
            ['2021-05-16 11:00'],  # expected_when_data
            ['-'],  # expected_meterings_data
            ['-'],  # expected_meal_data
            ['-'],  # expected_injections_data
            ['Foo; Bar'],  # expected_comments_data
        ],
        [
            'test_records_list_display_long_comment.yml',
            'admin',  # username
            ['2021-05-16 11:00'],  # expected_when_data
            ['-'],  # expected_meterings_data
            ['-'],  # expected_meal_data
            ['-'],  # expected_injections_data
            ['Just an incredi<...>'],  # expected_comments_data
        ],
    ],
)
def test_records_list_display(
        create_client,
        db_data,
        username,
        expected_when_data,
        expected_meterings_data,
        expected_meal_data,
        expected_injections_data,
        expected_comments_data,
):
    user = User.objects.get(username=username)

    client = create_client(
        authenticated_with=user,
    )
    response = client.get('/admin/sugar/record/')
    assert response.status_code == 200

    etree_html_parser = etree.HTMLParser()
    tree = etree.XML(
        text=response.content,
        parser=etree_html_parser,
    )

    when_search = '//table[@id="result_list"]/tbody/tr/th/a/text()'
    search_template = '//table[@id="result_list"]/tbody/tr/td[@class="{}"]/text()'  # noqa

    meterings_search = search_template.format('field-sugar_level')
    meal_search = search_template.format('field-total_meal')
    injections_search = search_template.format('field-injections_info')
    comments_search = search_template.format('field-short_comments')

    assert tree.xpath(when_search) == expected_when_data
    assert tree.xpath(meterings_search) == expected_meterings_data
    assert tree.xpath(meal_search) == expected_meal_data
    assert tree.xpath(injections_search) == expected_injections_data 
    assert tree.xpath(comments_search) == expected_comments_data 


@pytest.mark.parametrize(
    [
        'db_data_filename',
        'frozen_time',
        'display_type',
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
        # region display_type='change'
        [
            'test_change_display_basic.yml',  # db_data_filename
            None,  # frozen_time
            'change',  # display_type
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
            None,  # frozen_time
            'change',  # display_type
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
            None,  # frozen_time
            'change',  # display_type
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
            None,  # frozen_time
            'change',  # display_type
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
        # endregion
        # region display_type='add'
        [
            'test_add_display_basic.yml',  # db_data_filename
            None,  # frozen_time
            'add',  # display_type
            [],  # expected_date_data
            [],  # expected_time_data
            ['---------', '---------'],  # expected_pack_data
            ['---------'] * 2,  # expected_pack_options
            [],  # expected_meterings_data
            [],  # expected_meal_data
            [],  # expected_meal_description_data
            ['---------', '---------'],  # expected_syringes_data
            ['---------', '---------'],  # expected_syringes_options
            [],  # expected_injections_data
            ['', ''],  # expected_comments_data
        ],
        [
            'test_add_display_medication_options_actuality.yml',  # db_data_filename
            '2023-03-24T23:59:59.000+03:00',  # frozen_time
            'add',  # display_type
            [],  # expected_date_data
            [],  # expected_time_data
            ['---------', '---------'],  # expected_pack_data
            ['---------', 'Пачка тест-полосок от 2021-05-01', 'Пачка тест-полосок от 2023-03-16'] * 2,  # expected_pack_options
            [],  # expected_meterings_data
            [],  # expected_meal_data
            [],  # expected_meal_description_data
            ['---------', '---------'],  # expected_syringes_data
            ['---------', 'Шприц "Aspart" (300 ед.) от 2021-05-01', 'Шприц "Aspart" (300 ед.) от 2023-03-09'] * 2,  # expected_syringes_options
            [],  # expected_injections_data
            ['', ''],  # expected_comments_data
        ],
        [
            'test_add_display_medication_options_actuality.yml',  # db_data_filename
            '2023-03-25T00:00:00.000+03:00',  # frozen_time
            'add',  # display_type
            [],  # expected_date_data
            [],  # expected_time_data
            ['---------', '---------'],  # expected_pack_data
            ['---------', 'Пачка тест-полосок от 2021-05-01'] * 2,  # expected_pack_options
            [],  # expected_meterings_data
            [],  # expected_meal_data
            [],  # expected_meal_description_data
            ['---------', '---------'],  # expected_syringes_data
            ['---------', 'Шприц "Aspart" (300 ед.) от 2021-05-01'] * 2,  # expected_syringes_options
            [],  # expected_injections_data
            ['', ''],  # expected_comments_data
        ],
        # endregion
    ],
)
def test_add_or_change_display(
        create_client,
        db_data,
        freeze_time,
        display_type,
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
    client = create_client(
        authenticated_with=admin,
    )

    if display_type == 'change':
        record = models.Record.objects.get()
        url = f'/admin/sugar/record/{record.pk}/change/'
    elif display_type == 'add':
        url = '/admin/sugar/record/add/'
    else:
        raise NotImplementedError(f'Unknown display_type={display_type!r}')

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
