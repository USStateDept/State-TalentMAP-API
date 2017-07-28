import pytest

from model_mommy import mommy
from model_mommy.recipe import Recipe
from rest_framework import status


@pytest.fixture
def test_sharing_fixture():
    mommy.make('position.Position', id=2)


@pytest.mark.django_db()
@pytest.mark.parametrize("payload, resp", [
    ({}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "banana"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "email"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "email", "email": "a@a.c"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "email", "type": "position"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "email", "type": "position", "id": 1}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "email", "email": "a@a.c", "type": "banana"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "email", "email": "a@a.c", "type": "position", "id": 1}, status.HTTP_404_NOT_FOUND),
    ({"mode": "email", "email": "a@a.c", "type": "position", "id": 2}, status.HTTP_202_ACCEPTED),
    ({"mode": "internal"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "internal", "user": "a@a.c"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "internal", "id": 1, "type": "position"}, status.HTTP_400_BAD_REQUEST),
    ({"mode": "internal", "user": "a@a.c", "type": "position", "id": 1}, status.HTTP_501_NOT_IMPLEMENTED),
])
@pytest.mark.usefixtures("test_sharing_fixture")
def test_payload_validation(client, payload, resp):
    response = client.post("/api/v1/share/", payload)

    assert response.status_code == resp
