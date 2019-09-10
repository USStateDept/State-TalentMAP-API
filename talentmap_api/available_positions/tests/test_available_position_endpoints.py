import pytest
import json

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


@pytest.mark.django_db(transaction=True)
def test_highlight_action_endpoints(authorized_client, authorized_user):

    response = authorized_client.get(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # First, try to highlight without appropriate permissions
    response = authorized_client.put(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Now, try to unhiglight without appropriate permissions
    response = authorized_client.delete(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Add the permission to our user
    group = mommy.make('auth.Group', name='superuser')
    group.user_set.add(authorized_user)

    response = authorized_client.put(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.delete(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/available_position/{ap["cp_id"]}/highlight/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
def test_designation_action_endpoints(authorized_client, authorized_user):

    response = authorized_client.patch(f'/api/v1/available_position/{ap["cp_id"]}/designation/', data=json.dumps({"is_hard_to_fill": False}), content_type="application/json")

    assert response.status_code == status.HTTP_200_OK


