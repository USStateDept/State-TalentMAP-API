import pytest
import json

from model_mommy import mommy
from rest_framework import status

from talentmap_api.bidding.models import BidCycle


@pytest.fixture
def test_bidcycle_fixture():
    bidcycle = mommy.make(BidCycle, id=1, name="Bidcycle 1", cycle_start_date="2017-01-01", cycle_end_date="2018-01-01")
    for i in range(5):
        bidcycle.positions.add(mommy.make('position.Position'))


@pytest.mark.django_db(transaction=True)
def test_bidcycle_creation(authorized_client, authorized_user):
    assert BidCycle.objects.all().count() == 0

    response = authorized_client.post('/api/v1/bidcycle/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_end_date": "2088-01-01"
        }
    ), content_type='application/json')

    assert BidCycle.objects.all().count() == 1
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db(transaction=True)
def test_bidcycle_creation_validation(authorized_client, authorized_user):
    assert BidCycle.objects.all().count() == 0

    response = authorized_client.post('/api/v1/bidcycle/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_end_date": "1088-01-01"
        }
    ), content_type='application/json')

    assert BidCycle.objects.all().count() == 0
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_patch(authorized_client, authorized_user):
    response = authorized_client.patch('/api/v1/bidcycle/1/', data=json.dumps(
        {
            "name": "bidcycle",
            "cycle_start_date": "1988-01-01",
            "cycle_end_date": "2088-01-01",
            "active": True
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    assert BidCycle.objects.all().count() == 1
    cycle = BidCycle.objects.get(id=1)
    assert cycle.name == "bidcycle"
    assert str(cycle.cycle_start_date) == "1988-01-01"
    assert str(cycle.cycle_end_date) == "2088-01-01"
    assert cycle.active


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_patch_validation(authorized_client, authorized_user):
    response = authorized_client.patch('/api/v1/bidcycle/1/', data=json.dumps(
        {
            "cycle_end_date": "1088-01-01",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = authorized_client.patch('/api/v1/bidcycle/1/', data=json.dumps(
        {
            "cycle_start_date": "9999-01-01",
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_list_positions(authorized_client, authorized_user):
    response = authorized_client.get('/api/v1/bidcycle/1/positions/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 5


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidcycle_fixture")
def test_bidcycle_actions(authorized_client, authorized_user):
    position = mommy.make('position.Position')

    # Check the position is in the bidcycle
    response = authorized_client.get(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Add the position to the bidcycle
    response = authorized_client.put(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the position is in the bidcycle
    response = authorized_client.get(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Remove the position from the bidcycle
    response = authorized_client.delete(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check if the position is in the bidcycle
    response = authorized_client.get(f'/api/v1/bidcycle/1/position/{position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND