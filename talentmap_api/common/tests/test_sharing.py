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
