import pytest

from model_mommy import mommy
from rest_framework import status


@pytest.fixture
def test_field_params_fixture():
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    post = mommy.make('organization.Post')
    bidcycle.positions.add(mommy.make('position.Position', post=post))


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_inclusion(client):
    response = client.get('/api/v1/position/?include=post')

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data["results"][0].keys()) == ["post"]
    assert len(list(response.data["results"][0]["post"].keys())) > 1


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_child_inclusion(client):
    response = client.get('/api/v1/position/?include=post__id')

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data["results"][0].keys()) == ["post"]
    assert list(response.data["results"][0]["post"].keys()) == ["id"]


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_exclusion(client):
    response = client.get('/api/v1/position/?exclude=post')

    assert response.status_code == status.HTTP_200_OK
    assert "post" not in list(response.data["results"][0].keys())


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_child_exclusion(client):
    response = client.get('/api/v1/position/?exclude=post__id')

    assert response.status_code == status.HTTP_200_OK
    assert "post" in list(response.data["results"][0].keys())
    assert "id" not in list(response.data["results"][0]["post"].keys())
    assert list(response.data["results"][0]["post"].keys()) != []
