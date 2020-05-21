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

    response = authorized_client.get('/api/v1/client/statistics/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 0
    assert response.data["in_panel_clients"] == 0

    # Give users some bids
    position = mommy.make('position.Position')
    bidcycle = mommy.make('bidding.Bidcycle', active=True)
    bidcycle.positions.add(position)
    cp = mommy.make('bidding.CyclePosition', bidcycle=bidcycle, position=position)

    mommy.make('bidding.Bid', position=cp, bidcycle=bidcycle, user=clients[1], status="submitted")

    response = authorized_client.get('/api/v1/client/statistics/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 1
    assert response.data["bidding_no_handshake"] == 1
    assert response.data["in_panel_clients"] == 0

    # Give users some bids
    mommy.make('bidding.Bid', position=cp, bidcycle=bidcycle, user=clients[2], status="in_panel", handshake_offered_date="1999-01-01T00:00:00Z")

    response = authorized_client.get('/api/v1/client/statistics/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["all_clients"] == 10
    assert response.data["bidding_clients"] == 2
    assert response.data["bidding_no_handshake"] == 1
    assert response.data["in_panel_clients"] == 1

    # Test our filters
    response = authorized_client.get('/api/v1/client/?is_bidding=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = authorized_client.get('/api/v1/client/?is_bidding=false')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 8

    response = authorized_client.get('/api/v1/client/?is_bidding_no_handshake=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/client/?is_bidding_no_handshake=false')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/client/?is_in_panel=true')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/client/?is_in_panel=false')
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
def test_client_bid_list(authorized_client, authorized_user, test_clients_fixture):
    client = authorized_user.profile.direct_reports.first()

    position = mommy.make('position.Position')
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    bidcycle.positions.add(position)
    cp = mommy.make('bidding.CyclePosition', bidcycle=bidcycle, position=position)

    mommy.make('bidding.Bid', bidcycle=bidcycle, position=cp, user=client, status="draft", _quantity=10)

    response = authorized_client.get(f'/api/v1/client/{client.id}/bids/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db(transaction=True)
def test_client_waiver_list(authorized_client, authorized_user, test_clients_fixture):
    client = authorized_user.profile.direct_reports.first()

    position = mommy.make('position.Position')
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    bidcycle.positions.add(position)
    cp = mommy.make('bidding.CyclePosition', bidcycle=bidcycle, position=position)

    bid = mommy.make('bidding.Bid', bidcycle=bidcycle, position=cp, user=client, status="draft")
    mommy.make('bidding.Waiver', bid=bid, position=position, user=client, _quantity=10)

    response = authorized_client.get(f'/api/v1/client/{client.id}/waivers/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10
