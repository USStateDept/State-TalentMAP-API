from unittest.mock import Mock, patch
import pytest
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile

fake_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjpbIkNETyIsIkZTQmlkQ3ljbGVBZG1pbmlzdHJhdG9yIl0sInVuaXF1ZV9uYW1lIjoid2FzaGRjXFxhZG1pbiIsImRpc3BsYXlfbmFtZSI6ImFkbWluIiwiZW1haWwiOiJhZG1pbkBzdGF0ZS5nb3YiLCJzdWIiOjIsInN5c3RlbSI6IjMyIiwiaXNzIjoiSFIvRVgvU0REIiwiaWF0IjoxNTc5MDUyNTk4LCJuYmYiOjE1NzkwNTI2OTgsImV4cCI6MTU3OTk1MjU5OCwiYXVkIjoibG9jYWxob3N0OjMzMzMiLCJqdGkiOiJ0ZXN0LTEyMzQ1In0.bvKK5flTAQrzk7gfE4biNXTWZ-Ej1rWnvvs13FH6RIo"


@pytest.mark.django_db(transaction=True)
def test_employee_perdet_seq_num_actions(authorized_client, authorized_user):
    with patch('talentmap_api.fsbid.services.common.requests.get') as mock_get:
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {"Data": [{"perdet_seq_num": 1}], "return_code": 0}
        response = authorized_client.put('/api/v1/fsbid/employee/perdet_seq_num/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert UserProfile.objects.get(id=authorized_user.profile.id).emp_id == '1'

        mock_get.return_value.json.return_value = {}
        response = authorized_client.put('/api/v1/fsbid/employee/perdet_seq_num/', HTTP_JWT=fake_jwt)
        assert response.status_code == status.HTTP_204_NO_CONTENT
