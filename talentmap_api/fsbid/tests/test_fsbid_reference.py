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


@pytest.mark.django_db(transaction=True)
def test_fsbid_dangerpay(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        dangerpays = [{"pay_percent_num": 0, "code": 0, "description": "No danger pay"}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": dangerpays, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/dangerpay/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['id'] == dangerpays[0]['pay_percent_num']


@pytest.mark.django_db(transaction=True)
def test_fsbid_cycles(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        cycles = [{"cycle_id": 1, "cycle_name": "Cycle 1"}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": cycles, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/cycles/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['name'] == cycles[0]['cycle_name']


@pytest.mark.django_db(transaction=True)
def test_fsbid_bureaus(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        bureaus = [{"bur": "0001", "isregional": 1, "bureau_long_desc": "AFRICA", "bureau_short_desc": "AF"}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": bureaus, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/bureaus/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['code'] == bureaus[0]['bur']


@pytest.mark.django_db(transaction=True)
def test_fsbid_differentialrates(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        differentialrates = [{"pay_percent_num": 0, "pay_percentage_text": "Zero"}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": differentialrates, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/differentialrates/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['code'] == differentialrates[0]['pay_percent_num']


@pytest.mark.django_db(transaction=True)
def test_fsbid_grades(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        grades = [{"grade_code": 0}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": grades, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/grades/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['code'] == grades[0]['grade_code']


@pytest.mark.django_db(transaction=True)
def test_fsbid_languages(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        languages = [{"language_code": 0, "language_long_desc": "Spanish 1/1", "language_short_desc": 'QB 1/1'}]
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": languages, "return_code": 0}
        response = authorized_client.get('/api/v1/fsbid/reference/languages/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()[0]
        assert data['code'] == languages[0]['language_code']
