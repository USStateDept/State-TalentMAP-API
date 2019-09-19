import pytest
import datetime
from dateutil.relativedelta import relativedelta
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status
from django.utils import timezone


ap = {
    "cp_id": 89367,
    "cp_status": "OP",
    "cp_post_dt": "2020-08-02T00:00:00",
    "pos_title_desc": "CHIEF OF STAFF:",
    "pos_skill_code": "OC",
    "pos_location_code": "110010001",
    "post_org_country_state": "WASHINGTON, DISTRICT OF COLUMBIA",
    "ted": "2020-08-02T00:00:00",
    "fv_override_ted_date": "",
    "cycle_id": 21,
    "cycle_nm_txt": "Test Cycle",
    "bureau_code": "OC",
    "bsn_descr_text": "Summer 2020",
    "pos_skill_desc": "MANAGEMENT OFFICER",
    "pos_bureau_short_desc": 'Desc',
    "pos_job_category_desc": "Management",
    "pos_grade_code": "OC",
    "bureau_desc": "(A)BUREAU OF ADMINISTRATION",
    "lang1": "French(XX) 1/2",
    "lang2": "",
    "tod": "",
    "bt_differential_rate_num": "",
    "bt_danger_pay_num": "",
    "incumbent": "Siegner:",
    "position": "D0994900",
    "ppos_capsule_descr_txt": "ON SPEC.  The Bureau of Admnistration (A) is the back bone of all  dafdafafdadfadfadsfadfadfjfauoiukjigqur ijf iajfdpoiaudf afdoijafdiuwpei poiu foiafdjfd oau0jj;kj",
    "cp_ttl_bidder_qty": 0,
    "cp_at_grd_qty": 0,
    "cp_in_cone_qty": 0,
    "cp_at_grd_in_cone_qty": 0,
    "rnum": 1,
    "count(1)": 1
}

fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IldBU0hEQ1xcVEVTVFVTRVIifQ.o5o4XZ3Z_vsqqC4a2tGcGEoYu3sSYxej4Y2GcCQVtyE"


@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_available_positions_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": [ap]}
        response = authorized_client.get(f'/api/v1/fsbid/available_positions/', HTTP_JWT=fake_jwt)
        assert response.json()["results"][0]['id'] == [ap][0]['cp_id']


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_available_position_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": [ap]}
        response = authorized_client.get(f'/api/v1/fsbid/available_positions/{ap["cp_id"]}/', HTTP_JWT=fake_jwt)
        assert response.json()['id'] == ap['cp_id']

