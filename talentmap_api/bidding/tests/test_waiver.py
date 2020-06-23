import json
import pytest

from model_mommy import mommy
from rest_framework import status

from talentmap_api.bidding.models import Waiver


@pytest.mark.django_db(transaction=True)
def test_waiver_edit_methods(authorized_client, authorized_user):
    position = mommy.make("position.Position", id=1)
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    cp = mommy.make('bidding.CyclePosition', position=position, bidcycle=bidcycle)
    bid = mommy.make("bidding.Bid", user=authorized_user.profile, position=cp, status="draft", bidcycle=bidcycle)
    assert Waiver.objects.all().count() == 0

    response = authorized_client.post('/api/v1/waiver/', data=json.dumps(
        {
            "bid": bid.id,
            "position": 1,
            "description": "Partial French Waiver",
            "type": "partial",
            "category": "language"
        }
    ), content_type='application/json')

    assert Waiver.objects.all().count() == 1
    assert response.status_code == status.HTTP_201_CREATED

    waiver = Waiver.objects.all().first()

    response = authorized_client.patch(f'/api/v1/waiver/{waiver.id}/', data=json.dumps(
        {
            "description": "Partial French Waiver 2/2 -> 1/2"
        }
    ), content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    waiver.refresh_from_db()
    assert waiver.description == "Partial French Waiver 2/2 -> 1/2"


@pytest.mark.django_db(transaction=True)
def test_waiver_list_retrieve(authorized_client, authorized_user):
    position = mommy.make("position.Position", id=1)
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    cp = mommy.make('bidding.CyclePosition', position=position, bidcycle=bidcycle)
    bid = mommy.make("bidding.Bid", user=authorized_user.profile, position=cp, status="draft", bidcycle=bidcycle)
    mommy.make('bidding.Waiver', bid=bid, position=position, user=authorized_user.profile, _quantity=3)
    response = authorized_client.get('/api/v1/waiver/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3

    response = authorized_client.get(f'/api/v1/waiver/{Waiver.objects.first().id}/')

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("status,message_key,owner", [
    (Waiver.Status.approved, "approved_owner", True),
    (Waiver.Status.denied, "denied_owner", True),
    (Waiver.Status.requested, "requested_cdo", False),
])
@pytest.mark.django_db(transaction=True)
def test_waiver_notifications(status, message_key, owner, authorized_client, authorized_user):
    assert authorized_user.profile.notifications.count() == 0
    profile = authorized_user.profile

    if not owner:
        profile = mommy.make('auth.User').profile
        profile.cdo = authorized_user.profile
        profile.save()

    position = mommy.make("position.Position", id=1)
    bc = mommy.make('bidding.BidCycle')
    cp = mommy.make('bidding.CyclePosition', position=position, bidcycle=bc)
    bid = mommy.make("bidding.Bid", user=profile, position=cp, bidcycle=bc, status="draft")
    waiver = mommy.make('bidding.Waiver', bid=bid, position=position, user=profile)

    waiver.status = status
    waiver.save()

    assert authorized_user.profile.notifications.count() == 1
    assert authorized_user.profile.notifications.first().message == waiver.generate_status_messages()[message_key]
