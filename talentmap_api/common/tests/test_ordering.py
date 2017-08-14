import pytest
import json

from django.contrib.auth.models import User

from model_mommy import mommy
from model_mommy.recipe import Recipe
from rest_framework import status


@pytest.fixture
def test_ordering_position_fixture():
    post_1 = mommy.make('organization.Post', id=1, has_service_needs_differential=True)
    post_2 = mommy.make('organization.Post', id=2, has_service_needs_differential=False)

    position_1 = mommy.make('position.Position', id=1, post=post_1, position_number="1234")
    position_2 = mommy.make('position.Position', id=2, post=post_2, position_number="5678")


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_ordering_position_fixture")
def test_regular_ordering(client):
    response = client.get('/api/v1/position/?ordering=position_number')
    assert response.status_code == status.HTTP_200_OK

    assert response.data[0]["position_number"] == "1234"

    response = client.get('/api/v1/position/?ordering=-position_number')

    assert response.status_code == status.HTTP_200_OK

    assert response.data[0]["position_number"] == "5678"


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_ordering_position_fixture")
def test_nested_ordering(client):
    response = client.get('/api/v1/position/?ordering=post__has_service_needs_differential')
    assert response.status_code == status.HTTP_200_OK

    assert response.data[0]["position_number"] == "5678"

    response = client.get('/api/v1/position/?ordering=-post__has_service_needs_differential')

    assert response.status_code == status.HTTP_200_OK

    assert response.data[0]["position_number"] == "1234"
