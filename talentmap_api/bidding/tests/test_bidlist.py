import pytest
import datetime
import json
from dateutil.relativedelta import relativedelta

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
    assert response.data["results"][0]["position"]["id"] == in_cycle_position.id
    assert response.data["results"][0]["submission_date"] is None

    bid_id = response.data["results"][0]["id"]

    # Submit our bid
    response = authorized_client.put(f'/api/v1/bidlist/bid/{bid_id}/submit/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Get our bidlist, and validate that the position is now "submitted"
    response = authorized_client.get(f'/api/v1/bidlist/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["status"] == "submitted"
    assert response.data["results"][0]["position"]["id"] == in_cycle_position.id
    assert response.data["results"][0]["submission_date"] is not None

    # Try to delete our now submitted bid
    response = authorized_client.delete(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture")
def test_bidlist_patch_bid(authorized_client, authorized_user):
    bidcycle = BidCycle.objects.get(id=1)
    bureau = mommy.make('organization.Organization', code='12345')

    in_bureau_position = mommy.make('position.Position', bureau=bureau)
    out_of_bureau_position = mommy.make('position.Position', bureau=mommy.make('organization.Organization', code='asdfasd'))

    in_bureau_bid = mommy.make(Bid, user=mommy.make('auth.User').profile, position=in_bureau_position, bidcycle=bidcycle)
    out_of_bureau_bid = mommy.make(Bid, user=mommy.make('auth.User').profile, position=out_of_bureau_position, bidcycle=bidcycle)

    # Give our user appropriate permissions
    group = mommy.make('auth.Group', name='bureau_ao')
    group.user_set.add(authorized_user)
    group = mommy.make('auth.Group', name=f'bureau_ao_{bureau.code}')
    group.user_set.add(authorized_user)

    # Patch an in-bureau bid
    response = authorized_client.patch(f'/api/v1/bidlist/bid/{in_bureau_bid.id}/', data=json.dumps({
        "status": "handshake offered"
    }), content_type="application/json")

    assert response.status_code == status.HTTP_200_OK

    # Patch an out-of-bureau bid
    response = authorized_client.patch(f'/api/v1/bidlist/bid/{out_of_bureau_bid.id}/', data=json.dumps({
        "status": "handshake_offered"
    }), content_type="application/json")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture")
def test_bidlist_date_based_deletion(authorized_client, authorized_user):
    bidcycle = BidCycle.objects.get(id=1)

    # Create a direct report for us
    report = mommy.make('auth.User')
    report.profile.cdo = authorized_user.profile
    report.profile.save()

    '''
    Set up our timeline

         -2        Yesterday     Today     Tomorrow        +2
    [Start Date] [Bad Deadline] [TODAY] [Good Deadline] [End Date]
    '''

    start_date = (datetime.datetime.now().date() - relativedelta(days=2)).strftime('%Y-%m-%d')
    bad_deadline = (datetime.datetime.now().date() - relativedelta(days=1)).strftime('%Y-%m-%d')
    good_deadline = (datetime.datetime.now().date() + relativedelta(days=1)).strftime('%Y-%m-%d')
    end_date = (datetime.datetime.now().date() + relativedelta(days=2)).strftime('%Y-%m-%d')

    # Set our bidcycle dates
    bidcycle.cycle_start_date = start_date
    bidcycle.cycle_end_date = end_date
    bidcycle.cycle_deadline_date = good_deadline
    bidcycle.save()

    position = bidcycle.positions.first()

    # Create a bid for an unrelated user
    random_bid = mommy.make(Bid, user=mommy.make('auth.User').profile, position=position, bidcycle=bidcycle)

    # Try to close it - should return 403 because we don't own the bid and aren't CDO
    response = authorized_client.delete(f'/api/v1/bidlist/{random_bid.id}/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Create a bid for us
    our_bid = mommy.make(Bid, user=authorized_user.profile, position=position, bidcycle=bidcycle)

    # We should be able to delete it since we're still before the deadline
    response = authorized_client.delete(f'/api/v1/bidlist/{our_bid.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert authorized_user.profile.bidlist.count() == 1

    our_bid.refresh_from_db()
    assert our_bid.status == Bid.Status.closed
    our_bid.delete()

    # Re-create the bid as a submitted bid
    our_bid = mommy.make(Bid, status=Bid.Status.submitted, user=authorized_user.profile, position=position, bidcycle=bidcycle)

    # We should be able to delete it since we're still before the deadline
    response = authorized_client.delete(f'/api/v1/bidlist/{our_bid.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert authorized_user.profile.bidlist.count() == 1

    our_bid.refresh_from_db()
    assert our_bid.status == Bid.Status.closed
    our_bid.delete()

    # Re-create the bid as a handshake offered bid
    our_bid = mommy.make(Bid, status=Bid.Status.handshake_offered, user=authorized_user.profile, position=position, bidcycle=bidcycle)

    # We should be able to delete it since we're still before the deadline
    response = authorized_client.delete(f'/api/v1/bidlist/{our_bid.id}/')

    assert response.status_code == status.HTTP_403_FORBIDDEN
    our_bid.delete()

    # Change our deadline
    bidcycle.cycle_deadline_date = bad_deadline
    bidcycle.save()

    # Create a new bid for us
    our_bid = mommy.make(Bid, status=Bid.Status.submitted, user=authorized_user.profile, position=position, bidcycle=bidcycle)

    # Try to delete it, we should get a 403
    response = authorized_client.delete(f'/api/v1/bidlist/{our_bid.id}/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Create a direct report bid in this cycle
    report_bid = mommy.make(Bid, user=report.profile, position=position, bidcycle=bidcycle)

    # We should be able to delete (i.e., close) it because we are the CDO
    response = authorized_client.delete(f'/api/v1/bidlist/{report_bid.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert report.profile.bidlist.count() == 1
    assert report.profile.notifications.count() == 1
    assert report.profile.notifications.first().message == f"Bid {report_bid} has been closed by CDO {authorized_user.profile}"


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture")
def test_bidlist_max_submissions(authorized_client, authorized_user):
    bidcycle = BidCycle.objects.get(id=1)
    mommy.make(Bid, user=authorized_user.profile, bidcycle=bidcycle, status=Bid.Status.submitted, _quantity=10)

    bid = mommy.make(Bid, user=authorized_user.profile, bidcycle=bidcycle, status=Bid.Status.draft)

    # Submit our bid - this should fail as we will exceed the amount of allowable submissions!
    response = authorized_client.put(f'/api/v1/bidlist/bid/{bid.id}/submit/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
def test_bid_declined_notification(authorized_client, authorized_user, test_bidlist_fixture):
    assert authorized_user.profile.notifications.count() == 0

    bidcycle = BidCycle.objects.get(id=1)
    position = bidcycle.positions.first()
    bid = mommy.make(Bid, bidcycle=bidcycle, user=authorized_user.profile, position=position)

    bid.status = Bid.Status.declined
    bid.save()

    assert authorized_user.profile.notifications.count() == 1
    assert authorized_user.profile.notifications.first().message == f"Your bid for {position} has been declined."


@pytest.mark.django_db(transaction=True)
def test_bid_handshake_notification(authorized_client, authorized_user, test_bidlist_fixture):
    assert authorized_user.profile.notifications.count() == 0

    bidcycle = BidCycle.objects.get(id=1)
    position = bidcycle.positions.first()

    # Create this user's bid
    bid = mommy.make(Bid, bidcycle=bidcycle, user=authorized_user.profile, position=position)

    bid.status = Bid.Status.handshake_offered
    bid.save()

    assert authorized_user.profile.notifications.count() == 1
    assert authorized_user.profile.notifications.first().message == f"Your bid for {position} has been offered a handshake."


@pytest.mark.django_db(transaction=True)
def test_bid_other_handshake_notification(authorized_client, authorized_user, test_bidlist_fixture):
    assert authorized_user.profile.notifications.count() == 0

    bidcycle = BidCycle.objects.get(id=1)
    position = bidcycle.positions.first()

    competing_user = mommy.make('auth.User')
    assert competing_user

    # Create this user's bid
    mommy.make(Bid, bidcycle=bidcycle, user=authorized_user.profile, position=position)

    # Create a competing bid
    bid = mommy.make(Bid, bidcycle=bidcycle, user=competing_user.profile, position=position)

    bid.status = Bid.Status.handshake_offered
    bid.save()

    assert authorized_user.profile.notifications.count() == 1
    assert authorized_user.profile.notifications.first().message == f"A competing bid for {position} has been offered a handshake."
