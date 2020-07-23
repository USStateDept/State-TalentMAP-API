import json
import pytest

from model_mommy import mommy
from rest_framework import status

from talentmap_api.bidding.models import StatusSurvey


@pytest.mark.django_db(transaction=True)
def test_survey_creation(authorized_client, authorized_user):
    mommy.make("bidding.BidCycle", id=1)
    assert StatusSurvey.objects.all().count() == 0

    response = authorized_client.post('/api/v1/survey/', data=json.dumps(
        {
            "bidcycle": 1
        }
    ), content_type='application/json')

    assert StatusSurvey.objects.all().count() == 1
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db(transaction=True)
def test_survey_patch(authorized_client, authorized_user):
    survey = mommy.make("bidding.StatusSurvey", user=authorized_user.profile, id=1)
    assert not survey.is_differential_bidder

    response = authorized_client.patch('/api/v1/survey/1/', data=json.dumps(
        {
            "is_differential_bidder": True
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    survey.refresh_from_db()
    assert survey.is_differential_bidder


@pytest.mark.django_db()
def test_survey_list_retrieve(authorized_client, authorized_user):
    mommy.make("bidding.StatusSurvey", user=authorized_user.profile, id=1)
    response = authorized_client.get('/api/v1/survey/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/survey/1/')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db()
def test_survey_list_cdo(authorized_client, authorized_user):
    user = mommy.make('auth.User', username="client")
    user.profile.cdo = authorized_user.profile
    user.profile.save()

    mommy.make("bidding.StatusSurvey", user=user.profile, id=1)
    response = authorized_client.get(f'/api/v1/client/{user.profile.id}/survey/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["user"] == user.profile.id
    assert "calculated_values" in response.data["results"][0]
