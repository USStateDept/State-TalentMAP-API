import pytest

from unittest.mock import Mock, patch

from model_mommy import mommy
from rest_framework import status

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

@pytest.mark.django_db()
def test_favorite_action_endpoints(authorized_client, authorized_user):
   with patch('talentmap_api.fsbid.services.requests.get') as mock_get:
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = [pv]
      
      response = authorized_client.get(f'/api/v1/projected_vacancy/{pv["pos_id"]}/favorite/')

      assert response.status_code == status.HTTP_404_NOT_FOUND

      response = authorized_client.put(f'/api/v1/projected_vacancy/{pv["pos_id"]}/favorite/')

      assert response.status_code == status.HTTP_204_NO_CONTENT

      response = authorized_client.get(f'/api/v1/projected_vacancy/{pv["pos_id"]}/favorite/')

      assert response.status_code == status.HTTP_204_NO_CONTENT

      response = authorized_client.delete(f'/api/v1/projected_vacancy/{pv["pos_id"]}/favorite/')

      assert response.status_code == status.HTTP_204_NO_CONTENT

      response = authorized_client.get(f'/api/v1/projected_vacancy/{pv["pos_id"]}/favorite/')

      assert response.status_code == status.HTTP_404_NOT_FOUND
