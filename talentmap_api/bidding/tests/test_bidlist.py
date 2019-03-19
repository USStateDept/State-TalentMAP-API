import pytest
import datetime
from dateutil.relativedelta import relativedelta

from model_mommy import mommy
from rest_framework import status

from django.utils import timezone

from talentmap_api.bidding.models import BidCycle, Bid


@pytest.fixture
def test_bidlist_fixture():
    tour_of_duty = mommy.make("organization.TourOfDuty", months=24)
    post = mommy.make("organization.Post", tour_of_duty=tour_of_duty)
    bidcycle = mommy.make(BidCycle, id=1, name="Bidcycle 1", active=True)
    for i in range(5):
        bidcycle.positions.add(mommy.make('position.Position', post=post))
    

@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)


@pytest.mark.django_db(transaction=True)
def test_can_accept_new_bids_function(authorized_client, authorized_user, test_bidlist_fixture):
    active_cycle = BidCycle.objects.first()
    nonactive_cycle = mommy.make(BidCycle, id=2, active=False)

    in_cycle_position = active_cycle.positions.first()
    out_of_cycle_position = mommy.make('position.Position')

    assert in_cycle_position.can_accept_new_bids(active_cycle)[0]
    assert not out_of_cycle_position.can_accept_new_bids(active_cycle)[0]

    assert not in_cycle_position.can_accept_new_bids(nonactive_cycle)[0]


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture", "test_bidder_fixture")
def test_bidlist_position_actions(authorized_client, authorized_user):
    in_cycle_position = BidCycle.objects.first().positions.first()
    out_of_cycle_position = mommy.make('position.Position')

    # Check if our in cycle position is in the current user's bidlist
    response = authorized_client.get(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Put the position into the bidlist, but it will fail as we will be retired
    in_cycle_position.current_assignment = mommy.make("position.Assignment", position=in_cycle_position, user=authorized_user.profile, estimated_end_date="1999-01-01T00:00:00Z")
    in_cycle_position.save()
    profile = authorized_user.profile
    profile.mandatory_retirement_date = "1888-01-01T00:00:00Z"
    profile.save()
    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    profile.mandatory_retirement_date = "9999-01-01T00:00:00Z"
    profile.save()

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

    # Create a bid on the in_cycle_position
    bid = mommy.make("bidding.Bid", user=mommy.make('auth.User').profile, bidcycle=BidCycle.objects.first(), position=in_cycle_position, status=Bid.Status.handshake_offered)

    # Try to make a bid on a position with a handshake
    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    bid.status = Bid.Status.handshake_accepted
    bid.save()

    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    bid.status = Bid.Status.in_panel
    bid.save()

    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    bid.status = Bid.Status.approved
    bid.save()

    response = authorized_client.put(f'/api/v1/bidlist/position/{in_cycle_position.id}/')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_bidlist_fixture", "test_bidder_fixture")
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

    start_date = (timezone.now() - relativedelta(days=2))
    bad_deadline = (timezone.now() - relativedelta(days=1))
    good_deadline = (timezone.now() + relativedelta(days=1))
    end_date = (timezone.now() + relativedelta(days=2))

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

    # Create a new bid for us in handshake_offered
    our_bid = mommy.make(Bid, status=Bid.Status.handshake_offered, user=authorized_user.profile, position=position, bidcycle=bidcycle)

    # Try to delete it, we should get a 403
    response = authorized_client.delete(f'/api/v1/bidlist/{our_bid.id}/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Create a direct report bid in this cycle
    report_bid = mommy.make(Bid, user=report.profile, position=position, bidcycle=bidcycle)

    # We should be able to delete (i.e., close) it because we are the CDO
    response = authorized_client.delete(f'/api/v1/bidlist/{report_bid.id}/')
    report_bid.refresh_from_db()

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert report.profile.bidlist.count() == 1
    assert report.profile.notifications.count() == 1
    assert report.profile.notifications.first().message == f"Bid {report_bid} has been closed by CDO {authorized_user.profile}"


@pytest.mark.parametrize("status,message_key,owner", [
    (Bid.Status.handshake_offered, "handshake_offered_owner", True),
    (Bid.Status.handshake_offered, "handshake_offered_other", False),
    (Bid.Status.declined, "declined_owner", True),
    (Bid.Status.in_panel, "in_panel_owner", True),
    (Bid.Status.approved, "approved_owner", True),

])
@pytest.mark.django_db(transaction=True)
def test_bid_notifications(status, message_key, owner, authorized_client, authorized_user, test_bidlist_fixture):
    assert authorized_user.profile.notifications.count() == 0

    bidcycle = BidCycle.objects.get(id=1)
    position = bidcycle.positions.first()

    # Create this user's bid
    bid = mommy.make(Bid, bidcycle=bidcycle, user=authorized_user.profile, position=position)

    if not owner:
        # Create a competing bid
        bid = mommy.make(Bid, bidcycle=bidcycle, user=mommy.make('auth.User').profile, position=position)

    bid.status = status
    bid.save()

    assert authorized_user.profile.notifications.count() == 1
    assert authorized_user.profile.notifications.first().message == bid.generate_status_messages()[message_key]
