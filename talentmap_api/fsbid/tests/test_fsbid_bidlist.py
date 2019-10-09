import pytest
import datetime
from dateutil.relativedelta import relativedelta
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status
from django.utils import timezone

bid = {
    "perdet_seq_num": 2,
    "cycle_nm_txt": "Now & Winter 2018/2019",
    "cp_id": 1,
    "ptitle": "Political Officer",
    "pos_skill_code": "5505",
    "pos_skill_desc": "POLITICAL AFFAIRS",
    "pos_grade_code": "01",
    "ubw_hndshk_offrd_flg": "N",
    "ubw_hndshk_offrd_dt": "",
    "ubw_create_dt": "2019-02-04T09:44:31",
    "ubw_submit_dt": "2019-02-09T09:44:31",
    "bs_cd": "A",
    "bs_descr_txt": "Active",
    "cp_ttl_bidder_qty": 0,
    "cp_at_grd_qty": 0,
    "cp_in_cone_qty": 0,
    "cp_at_grd_in_cone_qty": 0,
    "location_city": "WASHINGTON",
    "location_state": "DC",
    "location_country": "USA"
  }

fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IldBU0hEQ1xcVEVTVFVTRVIifQ.o5o4XZ3Z_vsqqC4a2tGcGEoYu3sSYxej4Y2GcCQVtyE"

@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_bidlist_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.bid.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = [bid]
        response = authorized_client.get(f'/api/v1/fsbid/bidlist/', HTTP_JWT=fake_jwt)
        assert response.json()[0]['emp_id'] == [bid][0]['perdet_seq_num']


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_bidlist_position_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.bid.requests.get') as mock_get:
        # returns 404 when no position is found
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = []
        response = authorized_client.get(f'/api/v1/fsbid/bidlist/position/1/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # returns 204 when position is found
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = [bid]
        response = authorized_client.get(f'/api/v1/fsbid/bidlist/position/1/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    with patch('talentmap_api.fsbid.services.bid.requests.post') as mock_post:
        mock_post.return_value = Mock(ok=True)
        response = authorized_client.put(f'/api/v1/fsbid/bidlist/position/1/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    with patch('talentmap_api.fsbid.services.bid.requests.delete') as mock_del:
        mock_del.return_value = Mock(ok=True)
        response = authorized_client.delete(f'/api/v1/fsbid/bidlist/position/1/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_204_NO_CONTENT
