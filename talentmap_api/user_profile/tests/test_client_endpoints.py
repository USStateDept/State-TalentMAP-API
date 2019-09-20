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
def test_client_bid_counts(authorized_client, authorized_user, test_clients_fixture):
    client = authorized_user.profile.direct_reports.first()

    position = mommy.make('position.Position')
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    bidcycle.positions.add(position)
    cp = mommy.make('bidding.CyclePosition', bidcycle=bidcycle, position=position)

    statuses = list(Bid.Status.choices)

    status_counts = list(zip(range(1, len(statuses) + 1), statuses))

    for item in status_counts:
        mommy.make('bidding.Bid', bidcycle=bidcycle, position=cp, user=client, status=item[1][0], _quantity=item[0])

    expected_counts = {x[1][1]: x[0] for x in status_counts}

    # Delete a random bid
    random_bid = Bid.objects.all().order_by('?').first()
    expected_counts[random_bid.status] = expected_counts[random_bid.status] - 1
    random_bid.delete()

    response = authorized_client.get(f'/api/v1/client/{client.id}/')

    assert response.status_code == status.HTTP_200_OK

    for bid_status, count in expected_counts.items():
        assert response.data["bid_statistics"][0].get(bid_status) == count


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


@pytest.mark.django_db(transaction=True)
def test_client_bid_prepanel(authorized_client, authorized_user, test_clients_fixture):
    client = authorized_user.profile.direct_reports.first()
    lang_1 = mommy.make('language.Language', code="FR", long_description="French", short_description="French")
    lang_2 = mommy.make('language.Language', code="DE", long_description="German", short_description="German")
    qual_1 = mommy.make('language.Qualification', id=1, language=lang_1, spoken_proficiency__code="2", reading_proficiency__code="2+")
    qual_2 = mommy.make('language.Qualification', id=2, language=lang_2, spoken_proficiency__code="3", reading_proficiency__code="3+")

    position = mommy.make('position.Position')
    position.languages.add(*[qual_1, qual_2])
    client.language_qualifications.add(position.languages.first())
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    bidcycle.positions.add(position)
    cp = mommy.make('bidding.CyclePosition', bidcycle=bidcycle, position=position)

    bid = mommy.make('bidding.Bid', bidcycle=bidcycle, position=cp, user=client)

    response = authorized_client.get(f'/api/v1/client/{client.id}/bids/{bid.id}/prepanel/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["prepanel"] == "Bidder has not submitted a self-identification survey for this bidcycle"

    mommy.make('bidding.StatusSurvey', user=client, bidcycle=bidcycle)

    response = authorized_client.get(f'/api/v1/client/{client.id}/bids/{bid.id}/prepanel/')

    assert response.status_code == status.HTTP_200_OK
    prepanel = response.data["prepanel"]

    assert "language" in prepanel
    assert "skill" in prepanel
