import pytest

from rest_framework import status
from talentmap_api.user_profile.tests.mommy_recipes import client_for_profile


@pytest.fixture()
def test_clients_fixture():
    for _ in range(0, 10):
        client_for_profile()


@pytest.mark.django_db(transaction=True)
def test_client_list(authorized_client, authorized_user, test_clients_fixture):
    response = authorized_client.get('/api/v1/client/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db(transaction=True)
def test_client_retrieve(authorized_client, authorized_user, test_clients_fixture):
    client_id = authorized_user.profile.direct_reports.first().id
    response = authorized_client.get(f'/api/v1/client/{client_id}/')

    assert response.status_code == status.HTTP_200_OK
