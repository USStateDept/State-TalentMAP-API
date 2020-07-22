import json
import pytest

from unittest.mock import Mock, patch

from model_mommy import mommy
from rest_framework import status

from rest_framework_expiring_authtoken.models import ExpiringToken

from talentmap_api.user_profile.models import UserProfile


@pytest.fixture()
def test_user_profile_fixture():
    mommy.make("language.Qualification", id=1)
    mommy.make("language.Qualification", id=2)

    mommy.make("bidding.CyclePosition", id=1)
    mommy.make("bidding.CyclePosition", id=2)
    mommy.make("bidding.CyclePosition", id=3)


@pytest.mark.django_db(transaction=True)
def test_user_token_endpoint(authorized_client, authorized_user, test_user_profile_fixture):
    resp = authorized_client.get('/api/v1/accounts/token/view/')

    assert resp.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_user_public_profile_endpoint(authorized_client, authorized_user, test_user_profile_fixture):
    user_profile = UserProfile.objects.last()

    resp = authorized_client.get(f'/api/v1/profile/{user_profile.id}/')

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["first_name"] == user_profile.user.first_name

