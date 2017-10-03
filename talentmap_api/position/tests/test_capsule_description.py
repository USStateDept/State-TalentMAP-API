import pytest
import json

from talentmap_api.position.models import CapsuleDescription

from model_mommy import mommy
from rest_framework import status


@pytest.mark.django_db()
def test_capsule_description_creation(authorized_client, authorized_user):
    assert CapsuleDescription.objects.count() == 0

    response = authorized_client.post('/api/v1/capsule_description/', data=json.dumps(
        {
            "content": "Test content",
            "point_of_contact": "banana_vendor@state.gov",
            "website": "http://www.state.gov"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED
    assert CapsuleDescription.objects.count() == 1


@pytest.mark.django_db()
def test_capsule_description_update(authorized_client, authorized_user):
    mommy.make(CapsuleDescription, id=1, content="banana", point_of_contact="banana@state.gov", website="google it")

    response = authorized_client.patch('/api/v1/capsule_description/1/', data=json.dumps(
        {
            "content": "banana splits",
            "point_of_contact": "bananasplit@state.gov",
            "website": "http://www.state.gov"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    description = CapsuleDescription.objects.get(id=1)
    assert description.content == "banana splits"
    assert description.point_of_contact == "bananasplit@state.gov"
    assert description.website == "http://www.state.gov"
