import pytest
import datetime
from dateutil.relativedelta import relativedelta
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status
from django.utils import timezone

import talentmap_api.fsbid.services as services

pv = {
  "fv_seq_number": 89367,
  "post_title_desc": "CHIEF OF STAFF:",
  "pos_location_code": "110010001",
  "post_org_country_state": "WASHINGTON, DISTRICT OF COLUMBIA",
  "ted": "2020-08-02T00:00:00",
  "fv_override_ted_date": "",
  "bsn_id": 21,
  "bureau_code": "OC",
  "bsn_descr_text": "Summer 2020",
  "pos_skill_desc":  "MANAGEMENT OFFICER",
  "pos_job_category_desc":  "Management",
  "pos_crade_code": "OC",
  "bureau_desc": "(A)BUREAU OF ADMINISTRATION",
  "lang1": "",
  "lang2": "",
  "tod": "",
  "bt_differential_rate_num": "",
  "bt_danger_pay_num": "",
  "incumbent": "Siegner:",
  "position": "D0994900",
  "ppos_capsule_descr_txt": "ON SPEC.  The Bureau of Admnistration (A) is the back bone of all  dafdafafdadfadfadsfadfadfjfauoiukjigqur ijf iajfdpoiaudf afdoijafdiuwpei poiu foiafdjfd oau0jj;kj",
  "rnum": 1,
  "count(1)": 1
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
      mock_get.return_value.json.return_value = { "Data": [pv] }
      response = authorized_client.get(f'/api/v1/fsbid/projected_vacancies')
      assert response.json()["results"][0]['id'] == [pv][0]['fv_seq_number']
