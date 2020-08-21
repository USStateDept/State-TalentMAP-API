from unittest import skip

import pytest
import json

from model_mommy.recipe import seq
from model_mommy import mommy
from rest_framework import status


@pytest.fixture
def test_bidcycle_fixture(authorized_user):

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
