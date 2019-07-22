import pytest
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status

import talentmap_api.fsbid.services as services

bs = {
  "bsn_id": "1",
  "bsn_descr_text": "Test Bid Season",
  "bsn_start_date": "2020/01/01",
  "bsn_end_date": "2020/03/31",
  "bsn_panel_cutoff_date": "2020/04/15"
}

@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)

@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_bid_seasons_actions(authorized_client, authorized_user):
   with patch('talentmap_api.fsbid.services.requests.get') as mock_get:
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = [bs]
      response = authorized_client.get(f'/api/v1/fsbid/bid_seasons')
      assert response.json()[0]['id'] == [bs][0]['bsn_id']
