import pytest

from rest_framework import status

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
