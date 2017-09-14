import pytest
import json

from django.contrib.auth.models import User

from model_mommy import mommy
from rest_framework import status


@pytest.fixture
def test_sharing_fixture():
    mommy.make('position.Position', id=2)
    mommy.make('auth.User', username="test", email="test@state.gov")


@pytest.fixture
def test_sharing_update_fixture(authorized_user):
    mommy.make('position.Position', id=2)
    sending_user = mommy.make('auth.User', username="test", email="test@state.gov")
    mommy.make('messaging.Sharable',
               id=1,
               sharing_user=sending_user.profile,
               receiving_user=authorized_user.profile,
               sharable_model="position.Position",
               sharable_id=2)


@pytest.mark.django_db()
@pytest.mark.parametrize("payload, resp", [
    ({}, status.HTTP_400_BAD_REQUEST),
    ({"email": "a@a.c"}, status.HTTP_400_BAD_REQUEST),
    ({"type": "position"}, status.HTTP_400_BAD_REQUEST),
    ({"type": "position", "id": 1}, status.HTTP_400_BAD_REQUEST),
    ({"email": "a@a.c", "type": "banana"}, status.HTTP_400_BAD_REQUEST),
    ({"email": "a@a.c", "type": "position", "id": 1}, status.HTTP_404_NOT_FOUND),
    ({"email": "a@a.c", "type": "position", "id": 2}, status.HTTP_202_ACCEPTED),
    ({"email": "a@a.c"}, status.HTTP_400_BAD_REQUEST),
    ({"id": 1, "type": "position"}, status.HTTP_400_BAD_REQUEST),
    ({"email": "test@state.gov", "type": "position", "id": 1}, status.HTTP_404_NOT_FOUND),
    ({"email": "dne@state.gov", "type": "position", "id": 2}, status.HTTP_404_NOT_FOUND),
    ({"email": "test@state.gov", "type": "position", "id": 2}, status.HTTP_202_ACCEPTED),
])
@pytest.mark.usefixtures("test_sharing_fixture")
def test_payload_validation(authorized_client, authorized_user, payload, resp):
    response = authorized_client.post("/api/v1/share/", payload)

    assert response.status_code == resp


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_sharing_fixture")
def test_internal_share(authorized_client, authorized_user):
    user_profile = User.objects.get(email="test@state.gov").profile
    assert user_profile.received_shares.count() == 0

    response = authorized_client.post("/api/v1/share/", {
        "mode": "internal",
        "email": "test@state.gov",
        "type": "position",
        "id": 2
    })

    assert response.status_code == status.HTTP_202_ACCEPTED
    user_profile.refresh_from_db()
    assert user_profile.received_shares.count() == 1
    assert user_profile.notifications.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_sharing_update_fixture")
def test_update_internal_share(authorized_client, authorized_user):
    assert authorized_user.profile.received_shares.count() == 1
    share = authorized_user.profile.received_shares.first()
    assert not share.is_read

    response = authorized_client.patch(f"/api/v1/share/1/", data=json.dumps({
        "is_read": True
    }), content_type="application/json")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    share.refresh_from_db()
    assert share.is_read

    response = authorized_client.get(f"/api/v1/profile/", content_type="application/json")
    assert len(response.data["received_shares"]) == 1
