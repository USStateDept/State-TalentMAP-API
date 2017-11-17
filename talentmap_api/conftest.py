import pytest
from model_mommy import mommy


@pytest.fixture()
def authorized_user():
    user = mommy.make('auth.User', username="authorized_user")
    mommy.make('authtoken.Token', user=user, key="12345")

    return user


@pytest.fixture()
def authorized_client(client):
    client.defaults['HTTP_AUTHORIZATION'] = 'Token 12345'
    return client
