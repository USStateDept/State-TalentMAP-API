import pytest
import datetime
from dateutil.relativedelta import relativedelta
from model_mommy import mommy
from unittest.mock import Mock, patch
from rest_framework import status
from django.utils import timezone

import talentmap_api.fsbid.services as services

bid = { 
  "submittedDate": "2019/01/01",
  "statusCode": "A",
  "handshakeCode": "N",
  "cycle": { 
    "description" : "",
    "status": "A",
  }, 
  "employee": {
    "perdet_seq_num" : "1"
  }, 
  "cyclePosition": {
     "cp_id": 1,
     "status": "A",
     "pos_seq_num": "1",
     "totalBidders": 0,
     "atGradeBidders": 0,
     "inConeBidders": 0,
     "inBothBidders": 0,
  }

}

@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)

@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_bidlist_actions(authorized_client, authorized_user):
   with patch('talentmap_api.fsbid.services.requests.get') as mock_get:
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = [bid]
      response = authorized_client.get(f'/api/v1/fsbid/bidlist/')
      assert response.json()[0]['emp_id'] == [bid][0]['employee']['perdet_seq_num']

@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_bidlist_position_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.requests.get') as mock_get:
      # returns 404 when no position is found
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = []
      response = authorized_client.get(f'/api/v1/fsbid/bidlist/position/1/')
      assert response.status_code == status.HTTP_404_NOT_FOUND
      # returns 204 when position is found
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = [bid]
      response = authorized_client.get(f'/api/v1/fsbid/bidlist/position/1/')
      assert response.status_code == status.HTTP_204_NO_CONTENT
    
    with patch('talentmap_api.fsbid.services.requests.post') as mock_post:
      mock_post.return_value = Mock(ok=True)
      response = authorized_client.put(f'/api/v1/fsbid/bidlist/position/1/')
      assert response.status_code == status.HTTP_204_NO_CONTENT
    
    with patch('talentmap_api.fsbid.services.requests.delete') as mock_del:
      mock_del.return_value = Mock(ok=True)
      response = authorized_client.delete(f'/api/v1/fsbid/bidlist/position/1/')
      assert response.status_code == status.HTTP_204_NO_CONTENT
