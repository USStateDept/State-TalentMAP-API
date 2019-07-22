import pytest

from model_mommy import mommy
from rest_framework import status


@pytest.mark.django_db()
def test_favorite_action_endpoints(authorized_client, authorized_user):
    position = mommy.make_recipe('talentmap_api.bidding.tests.cycleposition')
    response = authorized_client.get(f'/api/v1/cycleposition/{position.id}/favorite/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = authorized_client.put(f'/api/v1/cycleposition/{position.id}/favorite/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/cycleposition/{position.id}/favorite/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.delete(f'/api/v1/cycleposition/{position.id}/favorite/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/cycleposition/{position.id}/favorite/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
