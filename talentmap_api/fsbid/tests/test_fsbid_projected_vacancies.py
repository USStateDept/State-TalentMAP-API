import pytest
import datetime
from dateutil.relativedelta import relativedelta
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status
from django.utils import timezone

import talentmap_api.fsbid.services as services

pv = {
  "pos_id": "1",
  "grade": "1",
  "skill": "1",
  "bureau": "Test Bureau",
  "organization": "Test Org",
  "tour_of_duty": "Test TED",
  "language1": "Lang 1",
  "reading_proficiency_1": "1",
  "spoken_proficiency_1": "1",
  "language_representation_1": "Lang Rep",
  "differential_rate": "0",
  "danger_pay": "N",
  "incumbent": "Test Incumbent",
  "ted": "01/1000",
  "position_number": "Test Position Number",
  "createDate": "2000-01-01",
  "title": "Test Title",
  "bsn_descr_text": "Test Bid Season",

}

@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)

@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_projected_vacancies_actions(authorized_client, authorized_user):
   with patch('talentmap_api.fsbid.services.requests.get') as mock_get:
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = { "positions": [pv], "pagination": { "count": 0, "limit": 0 } }
      response = authorized_client.get(f'/api/v1/fsbid/projected_vacancies')
      assert response.json()["results"][0]['id'] == [pv][0]['pos_id']
