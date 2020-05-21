import pytest

from model_mommy import mommy
from rest_framework import status


@pytest.fixture
def test_field_params_fixture():
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    post = mommy.make('organization.Post')
    position = mommy.make('position.Position', post=post)
    bidcycle.positions.add(position)
