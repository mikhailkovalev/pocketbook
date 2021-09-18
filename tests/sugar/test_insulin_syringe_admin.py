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

    with open('/home/mixon/.config/JetBrains/PyCharmCE2021.2/scratches/syringes_add.html', 'wb') as f:
        f.write(response.content)

    # etree_html_parser = etree.HTMLParser()
    # tree = etree.XML(
    #     text=response.content.decode('utf=8'),
    #     parser=etree_html_parser,
    # )