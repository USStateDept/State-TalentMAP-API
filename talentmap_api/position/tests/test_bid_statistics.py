import pytest

from talentmap_api.position.models import Position, Skill
from talentmap_api.bidding.models import Bid, BidCycle

from model_mommy import mommy


@pytest.fixture
def test_statistics_filter():
    mommy.make('position.Grade', id=1)
    mommy.make('position.Skill', id=1)
    position = mommy.make('position.Position', grade_id=1, skill_id=1)
    bidcycle = mommy.make('bidding.BidCycle', active=True, cycle_start_date="1900-01-01T00:00:00Z", cycle_deadline_date='9999-01-01T00:00:00Z', cycle_end_date='9999-01-01T00:00:00Z')
    bidcycle.positions.add(position)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("test_statistics_filter")
def test_bid_statistics(authorized_client, authorized_user):
    # In grade user
    in_grade = mommy.make("auth.User").profile
    in_grade.grade_id = 1
    in_grade.save()

    at_skill = mommy.make("auth.User").profile
    at_skill.skills.add(Skill.objects.get(id=1))
    at_skill.save()

    in_grade_at_skill = mommy.make("auth.User").profile
    in_grade_at_skill.grade_id = 1
    in_grade_at_skill.skills.add(Skill.objects.get(id=1))
    in_grade_at_skill.save()

    assert Position.objects.count() == 1
    assert BidCycle.objects.count() == 1

    position = Position.objects.all().first()
    bidcycle = BidCycle.objects.all().first()
    statistics = position.bid_statistics.first()

    assert statistics.total_bids == 0
    assert statistics.in_grade == 0
    assert statistics.at_skill == 0
    assert statistics.in_grade_at_skill == 0

    # Add a bid from a user in grade
    Bid.objects.create(user=in_grade, bidcycle=bidcycle, position=position)
    statistics.refresh_from_db()

    assert statistics.total_bids == 1
    assert statistics.in_grade == 1
    assert statistics.at_skill == 0
    assert statistics.in_grade_at_skill == 0

    # Add a bid from a user at skill
    Bid.objects.create(user=at_skill, bidcycle=bidcycle, position=position)
    statistics.refresh_from_db()

    assert statistics.total_bids == 2
    assert statistics.in_grade == 1
    assert statistics.at_skill == 1
    assert statistics.in_grade_at_skill == 0

    # Add a bid from a user at skill and in grade
    bid = Bid.objects.create(user=in_grade_at_skill, bidcycle=bidcycle, position=position)
    statistics.refresh_from_db()

    assert statistics.total_bids == 3
    assert statistics.in_grade == 2
    assert statistics.at_skill == 2
    assert statistics.in_grade_at_skill == 1

    # Delete a bid
    bid.delete()
    statistics.refresh_from_db()
    assert statistics.total_bids == 2
    assert statistics.in_grade == 1
    assert statistics.at_skill == 1
    assert statistics.in_grade_at_skill == 0
