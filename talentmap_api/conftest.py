import pytest
from model_mommy import mommy
from django.conf import settings


@pytest.fixture()
def authorized_user():
    user = mommy.make('auth.User', username="authorized_user")
    mommy.make('authtoken.Token', user=user, key="12345")

    return user


@pytest.fixture()
def authorized_client(client):
    client.defaults['HTTP_AUTHORIZATION'] = 'Token 12345'
    return client


def pytest_configure():
    test_cache = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    settings.CACHES = test_cache
