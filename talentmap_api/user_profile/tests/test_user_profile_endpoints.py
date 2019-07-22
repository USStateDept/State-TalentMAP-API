import pytest
import json

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

@pytest.mark.django_db(transaction=True)
def test_user_profile_current_assignment(authorized_client, authorized_user, test_user_profile_fixture):
    resp = authorized_client.get('/api/v1/profile/')

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["current_assignment"] is None

    mommy.make('position.Assignment', position=mommy.make('position.Position', id=5), user=authorized_user.profile, tour_of_duty=mommy.make('organization.TourOfDuty'), start_date="1991-01-01T00:00:00Z")

    resp = authorized_client.get('/api/v1/profile/')

    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["current_assignment"] is not None


@pytest.mark.django_db(transaction=True)
def test_user_profile_retirement_date(authorized_client, authorized_user, test_user_profile_fixture):
    resp = authorized_client.patch('/api/v1/profile/', data=json.dumps({
        "date_of_birth": "1000-01-01T00:00:00Z"
    }), content_type="application/json")

    assert resp.status_code == status.HTTP_200_OK

    resp = authorized_client.get('/api/v1/profile/')
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["mandatory_retirement_date"] == "1065-01-01T00:00:00Z"


@pytest.mark.django_db(transaction=True)
def test_user_profile_favorites(authorized_client, authorized_user, test_user_profile_fixture):
    resp = authorized_client.get('/api/v1/profile/')

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["favorite_positions"]) == 0
    assert len(resp.data["language_qualifications"]) == 0

    resp = authorized_client.patch('/api/v1/profile/', data=json.dumps({
        "favorite_positions": [1, 3],
        "language_qualifications": [1]
    }), content_type="application/json")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["favorite_positions"]) == 2
    assert len(resp.data["language_qualifications"]) == 1

    assert list(authorized_user.profile.favorite_positions.values_list("id", flat=True)) == [1, 3]
    assert list(authorized_user.profile.language_qualifications.values_list("id", flat=True)) == [1]

    resp = authorized_client.patch('/api/v1/profile/', data=json.dumps({
        "favorite_positions": [2],
        "language_qualifications": [2]
    }), content_type="application/json")

    assert resp.status_code == status.HTTP_200_OK
    assert len(resp.data["favorite_positions"]) == 1
    assert len(resp.data["language_qualifications"]) == 1

    assert list(authorized_user.profile.favorite_positions.values_list("id", flat=True)) == [2]
    assert list(authorized_user.profile.language_qualifications.values_list("id", flat=True)) == [2]
