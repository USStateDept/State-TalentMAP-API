from unittest.mock import Mock, patch
import pytest
from model_mommy import mommy

bs = {
    "bsn_id": "1",
    "bsn_descr_text": "Test Bid Season",
    "bsn_start_date": "2020/01/01",
    "bsn_end_date": "2020/03/31",
    "bsn_panel_cutoff_date": "2020/04/15"
}

fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IldBU0hEQ1xcVEVTVFVTRVIifQ.o5o4XZ3Z_vsqqC4a2tGcGEoYu3sSYxej4Y2GcCQVtyE"


@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidder_fixture")
def test_bid_seasons_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.bid_season.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": [bs], "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/bid_seasons/', HTTP_JWT=fake_jwt)
        assert response.json()[0]['id'] == [bs][0]['bsn_id']
