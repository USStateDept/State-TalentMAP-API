import pytest
import datetime
import json

from model_mommy import mommy
from rest_framework import status
from dateutil import relativedelta

from django.utils import timezone
from talentmap_api.bidding.models import BidCycle, Bid


@pytest.fixture
def test_bidlist_fixture():
    bidcycle = mommy.make(BidCycle, id=1, name="Bidcycle 1", active=True)
    for i in range(5):
        bidcycle.positions.add(mommy.make('position.Position'))


@pytest.fixture
def test_bidder_fixture(authorized_user):
    group = mommy.make('auth.Group', name='bidder')
    group.user_set.add(authorized_user)
