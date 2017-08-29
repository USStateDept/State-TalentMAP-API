import pytest

from model_mommy import mommy
from rest_framework import status


@pytest.fixture
def test_field_params_fixture():
    description = mommy.make('position.CapsuleDescription')
    position = mommy.make('position.Position', description=description)


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_inclusion(client):
    response = client.get('/api/v1/position/?include=description')

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data["results"][0].keys()) == ["description"]
    assert len(list(response.data["results"][0]["description"].keys())) > 1


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_child_inclusion(client):
    response = client.get('/api/v1/position/?include=description__id')

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data["results"][0].keys()) == ["description"]
    assert list(response.data["results"][0]["description"].keys()) == ["id"]


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_exclusion(client):
    response = client.get('/api/v1/position/?exclude=description')

    assert response.status_code == status.HTTP_200_OK
    assert "description" not in list(response.data["results"][0].keys())


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_field_params_fixture")
def test_field_child_exclusion(client):
    response = client.get('/api/v1/position/?exclude=description__id')

    assert response.status_code == status.HTTP_200_OK
    assert "description" in list(response.data["results"][0].keys())
    assert "id" not in list(response.data["results"][0]["description"].keys())
    assert list(response.data["results"][0]["description"].keys()) != []
