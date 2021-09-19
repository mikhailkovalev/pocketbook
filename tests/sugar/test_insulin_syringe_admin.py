from unittest.mock import ANY

import pytest
from lxml import (
    etree,
)


@pytest.fixture
def foo_insulin_kind(
        create_insulin_kind,
):
    return create_insulin_kind(name='Foo')


@pytest.fixture
def bar_insulin_kind(
        create_insulin_kind,
):
    return create_insulin_kind(name='Bar')


def test_add_record(
        admin,
        bar_insulin_kind,
        create_client,
        foo_insulin_kind,
):
    url = '/admin/sugar/insulinsyringe/add/'
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

    insulin_kind_value = tree.xpath(
        '//div[@class="form-row field-insulin_mark"]'
        '/div'
        '/div'
        '/select[@id="id_insulin_mark"]'
        '/option[@selected]'
        '/text()'
    )
    assert insulin_kind_value == [
        '---------',
    ]

    volume_value = tree.xpath(
        '//div[@class="form-row field-volume"]'
        '/div'
        '/input'
        '/@value'
    )
    assert volume_value == []

    opening_value = tree.xpath(
        '//div[@class="form-row field-opening"]'
        '/div'
        '/input'
        '/@value'
    )
    assert opening_value == []

    expiry_plan_value = tree.xpath(
        '//div[@class="form-row field-expiry_plan"]'
        '/div'
        '/input'
        '/@value'
    )
    assert expiry_plan_value == []

    expiry_actual_value = tree.xpath(
        '//div[@class="form-row field-expiry_actual"]'
        '/div'
        '/input'
        '/@value'
    )
    assert expiry_actual_value == []
