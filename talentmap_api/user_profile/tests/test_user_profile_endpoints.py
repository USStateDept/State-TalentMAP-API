import pytest
import json

from model_mommy import mommy
from rest_framework import status


@pytest.fixture()
def test_user_profile_fixture():
    mommy.make("language.Qualification", id=1)
    mommy.make("language.Qualification", id=2)

    mommy.make("position.Position", id=1)
    mommy.make("position.Position", id=2)
    mommy.make("position.Position", id=3)


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
