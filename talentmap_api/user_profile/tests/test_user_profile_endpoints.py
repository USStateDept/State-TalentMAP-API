import pytest
import json

from unittest.mock import Mock, patch

from model_mommy import mommy
from rest_framework import status

from rest_framework_expiring_authtoken.models import ExpiringToken

from talentmap_api.user_profile.models import UserProfile


@pytest.mark.django_db(transaction=True)
def test_user_token_endpoint(authorized_client, authorized_user):
    resp = authorized_client.get('/api/v1/accounts/token/view/')

    assert resp.status_code == status.HTTP_200_OK

@pytest.mark.django_db(transaction=True)
def test_user_public_profile_endpoint(authorized_client, authorized_user):
    user_profile = UserProfile.objects.last()

    resp = authorized_client.get(f'/api/v1/profile/{user_profile.id}/')

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["first_name"] == user_profile.user.first_name


@pytest.mark.django_db(transaction=True)
def test_user_profile_favorites(authorized_client, authorized_user):
     with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": []}
        resp = authorized_client.get('/api/v1/profile/')

        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data["favorite_positions"]) == 0
