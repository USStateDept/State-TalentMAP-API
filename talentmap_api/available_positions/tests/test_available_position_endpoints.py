import pytest

from unittest.mock import Mock, patch

from model_mommy import mommy
from rest_framework import status

ap = {
  "cp_id": "1",
}

@pytest.mark.django_db()
def test_favorite_action_endpoints(authorized_client, authorized_user):
   with patch('talentmap_api.fsbid.services.available_positions.requests.get') as mock_get:
      mock_get.return_value = Mock(ok=True)
      mock_get.return_value.json.return_value = [ap]
      
      response = authorized_client.get(f'/api/v1/available_position/{ap["cp_id"]}/favorite/')

      assert response.status_code == status.HTTP_404_NOT_FOUND

      response = authorized_client.put(f'/api/v1/available_position/{ap["cp_id"]}/favorite/')

      assert response.status_code == status.HTTP_204_NO_CONTENT

      response = authorized_client.get(f'/api/v1/available_position/{ap["cp_id"]}/favorite/')

      assert response.status_code == status.HTTP_204_NO_CONTENT

      response = authorized_client.delete(f'/api/v1/available_position/{ap["cp_id"]}/favorite/')

      assert response.status_code == status.HTTP_204_NO_CONTENT

      response = authorized_client.get(f'/api/v1/available_position/{ap["cp_id"]}/favorite/')

      assert response.status_code == status.HTTP_404_NOT_FOUND
