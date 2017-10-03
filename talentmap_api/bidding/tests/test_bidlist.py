import pytest

from model_mommy import mommy
from rest_framework import status

from talentmap_api.bidding.models import BidCycle, Bid


@pytest.fixture
def test_bidlist_fixture():
    bidcycle = mommy.make(BidCycle, id=1, name="Bidcycle 1", active=True)
    for i in range(5):
        bidcycle.positions.add(mommy.make('position.Position'))


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture")
def test_bidlist_position_actions(authorized_client, authorized_user):
    in_cycle_position = BidCycle.objects.first().positions.first()
    out_of_cycle_position = mommy.make('position.Position')

    # Check if our in cycle position is in the current user's bidlist
    response = authorized_client.get(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Put the position into the bidlist
    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Validate it is now in the list
    response = authorized_client.get(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Remove the position from the list
    response = authorized_client.delete(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Validate it was removed
    response = authorized_client.get(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Attempt to add an out of cycle position
    response = authorized_client.put(f'/api/v1/bidlist/position/{out_of_cycle_position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture")
def test_bidlist_bid_actions(authorized_client, authorized_user):
    in_cycle_position = BidCycle.objects.first().positions.first()

    # Put the position into the bidlist
    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Get our bidlist, and validate that the position is in the list as a draft
    response = authorized_client.get(f'/api/v1/bidlist/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["status"] == "draft"
    assert response.data["results"][0]["position"] == str(in_cycle_position)
    assert response.data["results"][0]["submission_date"] is None

    bid_id = response.data["results"][0]["id"]

    # Submit our bid
    response = authorized_client.put(f'/api/v1/bidlist/bid/{bid_id}/submit/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Get our bidlist, and validate that the position is now "submitted"
    response = authorized_client.get(f'/api/v1/bidlist/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["status"] == "submitted"
    assert response.data["results"][0]["position"] == str(in_cycle_position)
    assert response.data["results"][0]["submission_date"] is not None

    # Try to delete our now submitted bid
    response = authorized_client.delete(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture")
def test_bidlist_max_submissions(authorized_client, authorized_user):
    mommy.make(Bid, user=authorized_user.profile, status=Bid.Status.submitted, _quantity=10)

    bid = mommy.make(Bid, user=authorized_user.profile, status=Bid.Status.draft)

    # Submit our bid - this should fail as we will exceed the amount of allowable submissions!
    response = authorized_client.put(f'/api/v1/bidlist/bid/{bid.id}/submit/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
