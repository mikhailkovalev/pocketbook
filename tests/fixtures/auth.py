import pytest
from django.contrib.auth.models import (
    User,
)
from django.test import (
    Client,
)


@pytest.fixture
def create_user():
    def _create_user(
            username='user',
            is_staff=False,
            is_superuser=False,
            password=None,
            **kwargs,
    ):
        if password is None:
            password = username

        user = User(
            username=username,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **kwargs,
        )
        user.set_password(password)
        user.save()
        return user

    return _create_user


@pytest.fixture
def admin(
        transactional_db,
        create_user,
):
    return create_user(
        username='admin',
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def create_client():
    def _create_client(
            authenticated_with=None,
            password=None,
    ):
        client = Client()
        if authenticated_with is not None:
            response = client.post(
                path='/admin/login/',
                data={
                    'username': authenticated_with.username,
                    'password': password or authenticated_with.username,
                },
            )
            client.cookies['sessionid'] = response.cookies['sessionid']

        return client

    return _create_client

