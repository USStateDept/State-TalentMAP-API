import pytest

from model_mommy import mommy

from rest_framework import status
from talentmap_api.user_profile.tests.mommy_recipes import client_for_profile

from talentmap_api.bidding.models import Bid


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


@pytest.mark.django_db(transaction=True)
def test_client_bid_counts(authorized_client, authorized_user, test_clients_fixture):
    client = authorized_user.profile.direct_reports.first()

    position = mommy.make('position.Position')
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    bidcycle.positions.add(position)

    statuses = list(Bid.Status.choices)

    status_counts = list(zip(range(1, len(statuses) + 1), statuses))

    for item in status_counts:
        mommy.make('bidding.Bid', bidcycle=bidcycle, position=position, user=client, status=item[1], _quantity=item[0])

    response = authorized_client.get(f'/api/v1/client/{client.id}/')

    assert response.status_code == status.HTTP_200_OK

    expected_counts = {x[1][1]: x[0] for x in status_counts}

    assert response.data["bid_information"] == expected_counts
