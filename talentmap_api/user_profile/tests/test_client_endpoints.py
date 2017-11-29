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
def test_client_statistics(authorized_client, authorized_user, test_clients_fixture):
    response = authorized_client.get('/api/v1/client/statistics/')
    clients = list(authorized_user.profile.direct_reports.all())

    # Everything should be empty except for "all_clients"
    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 0
    assert response.data["in_panel_clients"] == 0
    assert response.data["on_post_clients"] == 0

    # Give a user an assignment
    mommy.make('position.Assignment', user=clients[0])

    response = authorized_client.get('/api/v1/client/statistics/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 0
    assert response.data["in_panel_clients"] == 0
    assert response.data["on_post_clients"] == 1

    # Give users some bids
    position = mommy.make('position.Position')
    bidcycle = mommy.make('bidding.Bidcycle')
    bidcycle.positions.add(position)
    mommy.make('bidding.Bid', position=position, bidcycle=bidcycle, user=clients[1], status="submitted")

    response = authorized_client.get('/api/v1/client/statistics/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 1
    assert response.data["in_panel_clients"] == 0
    assert response.data["on_post_clients"] == 1

    # Give users some bids
    mommy.make('bidding.Bid', position=position, bidcycle=bidcycle, user=clients[2], status="in_panel")

    response = authorized_client.get('/api/v1/client/statistics/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 2
    assert response.data["in_panel_clients"] == 1
    assert response.data["on_post_clients"] == 1

    # Test our filters
    response = authorized_client.get('/api/v1/client/?is_bidding=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = authorized_client.get('/api/v1/client/?is_bidding=false')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 8

    response = authorized_client.get('/api/v1/client/?is_in_panel=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/client/?is_in_panel=false')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 9

    response = authorized_client.get('/api/v1/client/?is_on_post=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/client/?is_on_post=false')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 9


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
        mommy.make('bidding.Bid', bidcycle=bidcycle, position=position, user=client, status=item[1][0], _quantity=item[0])

    response = authorized_client.get(f'/api/v1/client/{client.id}/')

    assert response.status_code == status.HTTP_200_OK

    expected_counts = {x[1][1]: x[0] for x in status_counts}

    for bid_status, count in expected_counts.items():
        assert response.data["bid_statistics"][0].get(bid_status) == count
