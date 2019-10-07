import pytest
import datetime
from dateutil.relativedelta import relativedelta
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status
from django.utils import timezone

bid = {
    "check_ind": False,
    "delete_ind": False,
    "per_seq_num": 2,
    "per_full_name": "EBERLY-HARNICAR,RIOVON-CZORNY NMN",
    "cycle_nm_txt": "Now & Winter 2018/2019",
    "cs_cd": "A",
    "cs_descr_txt": "Active",
    "cc_cd": "O",
    "cc_descr_txt": "Other",
    "cp_id": 1,
    "pos_seq_num": 53960,
    "pos_bureau_code": "130000",
    "pos_bureau_short_desc": "EAP",
    "pos_org_code": "330501",
    "pos_org_short_desc": "BEIJING",
    "pos_num_text": "10231180",
    "ptitle": "Political Officer",
    "pos_skill_code": "5505",
    "pos_skill_desc": "POLITICAL AFFAIRS",
    "pos_grade_code": "02",
    "ted": None,
    "ubw_core_bid_ind": "N",
    "ubw_core_bid_desc": "No",
    "bp_code": "M",
    "bp_descr_txt": "Medium",
    "ubw_rank_num": None,
    "ubw_submit_dt": "2019-02-04T09:44:31",
    "hs_code": None,
    "ubw_hndshk_offrd_flg": "N",
    "ubw_hndshk_offrd_dt": None,
    "bs_cd": "A",
    "bs_descr_txt": "Active",
    "cps_descr_txt": "Open",
    "bid_count": "<span data-ct=\"001\">1(0/0)0</span>",
    "pos_lang_code": None,
    "pos_lang_desc": None,
    "acp_hard_to_fill_ind": "N",
    "cp_critical_need_ind": "N",
    "pct_short_desc_text": " ",
    "pct_desc_text": " ",
    "ubw_comment": None,
    "bid_unavailable_ind": "N",
    "jo_pos_ind": "N",
    "bid_due_date_passed": "Y",
    "capsule_position_desc": "<a title=\"The East Asia and Pacific Hub director plans and implements to engage...\" href=\"#\">60822100</a>",
    "famer_link": "<a title=\"Click to view Famer Page\" href=\"#\">fmr</a>",
    "bidding_tool": "<a data-pn=\"10231180\" title=\"Click to view Capsule Description and Bidding Tool\" href=\"#\">10231180</a>",
    "cycle_bidders": "<a title=\"Click to view Cycle Bidder\" href=\"#\">cb</a>",
    "tp_codes": None
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
        assert response.json()[0]['emp_id'] == [bid][0]['per_seq_num']


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
