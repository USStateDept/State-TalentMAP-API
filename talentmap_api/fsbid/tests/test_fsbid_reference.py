from unittest.mock import Mock, patch
import pytest
from rest_framework import status

fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IldBU0hEQ1xcVEVTVFVTRVIifQ.o5o4XZ3Z_vsqqC4a2tGcGEoYu3sSYxej4Y2GcCQVtyE"


@pytest.mark.django_db(transaction=True)
def test_fsbid_locations(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        locations = [{"location_code": '12345', "location_city": "Washington", "location_state": "DC", "location_country": "United States", "is_domestic": 1}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": locations, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/locations/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['code'] == locations[0]['location_code']
        assert data['is_domestic'] is True
