from unittest import skip

import pytest
import json

from model_mommy.recipe import seq
from model_mommy import mommy
from rest_framework import status

from talentmap_api.bidding.models import BidCycle, Bid
from talentmap_api.position.models import PositionBidStatistics
from talentmap_api.user_profile.models import SavedSearch


@pytest.fixture
def test_bidcycle_fixture(authorized_user):
    bidcycle = mommy.make(BidCycle, id=1, name="Bidcycle 1", cycle_start_date="2017-01-01T00:00:00Z", cycle_deadline_date="2017-05-05T00:00:00Z", cycle_end_date="2018-01-01T00:00:00Z", active=True)
    for i in range(5):
        pos = mommy.make('position.Position', position_number=seq("2"))
        bidcycle.positions.add(pos)

    # Create 5 "in search" positions
    mommy.make('position.Position', position_number=seq("56"), _quantity=5)
    mommy.make('position.Position', position_number=seq("1"), _quantity=2)

    mommy.make('user_profile.SavedSearch',
               id=1,
               name="Test search",
               owner=authorized_user.profile,
               endpoint='/api/v1/position/',
               filters={
                   "position__position_number__startswith": ["56"],
               })

    # A non-position search
    mommy.make('user_profile.SavedSearch',
               id=2,
               name="Test search",
               owner=authorized_user.profile,
               endpoint='/api/v1/orgpost/',
               filters={
                   "differential_rate__gt": ["0"],
               })
