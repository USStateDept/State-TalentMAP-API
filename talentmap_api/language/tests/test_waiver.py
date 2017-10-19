import pytest
import json

from model_mommy import mommy
from rest_framework import status

from talentmap_api.language.models import Waiver


@pytest.mark.django_db(transaction=True)
def test_waiver_creation(authorized_client, authorized_user):
    mommy.make("bidding.BidCycle", id=1)
    mommy.make("language.Language", id=1)
    mommy.make("position.Position", id=1)
    assert Waiver.objects.all().count() == 0

    response = authorized_client.post('/api/v1/language_waiver/', data=json.dumps(
        {
            "position": 1,
            "language": 1,
            "bidcycle": 1
        }
    ), content_type='application/json')

    assert Waiver.objects.all().count() == 1
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db(transaction=True)
def test_waiver_patch(authorized_client, authorized_user):
    waiver = mommy.make("language.Waiver", user=authorized_user.profile, id=1)
    assert waiver.type == "full"

    response = authorized_client.patch('/api/v1/language_waiver/1/', data=json.dumps(
        {
            "type": "partial"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    waiver.refresh_from_db()
    assert waiver.type == "partial"


@pytest.mark.django_db()
def test_waiver_list_retrieve(authorized_client, authorized_user):
    mommy.make("language.Waiver", user=authorized_user.profile, id=1)
    response = authorized_client.get('/api/v1/language_waiver/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/language_waiver/1/')

    assert response.status_code == status.HTTP_200_OK
