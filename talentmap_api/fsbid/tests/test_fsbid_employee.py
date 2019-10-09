import pytest
from unittest.mock import Mock, patch
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile

fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IldBU0hEQ1xcVEVTVFVTRVIifQ.o5o4XZ3Z_vsqqC4a2tGcGEoYu3sSYxej4Y2GcCQVtyE"

@pytest.mark.django_db(transaction=True)
def test_employee_perdet_seq_num_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": [{"perdet_seq_num": 1}]}
        response = authorized_client.put('/api/v1/fsbid/employee/perdet_seq_num/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert UserProfile.objects.get(id=authorized_user.profile.id).emp_id == '1'

        mock_get.return_value.json.return_value = {}
        response = authorized_client.put('/api/v1/fsbid/employee/perdet_seq_num/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        

