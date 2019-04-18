from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.bidding.models import BidCycle
from talentmap_api.position.models import Position, Grade, Skill, Classification, Assignment
from talentmap_api.organization.tests.mommy_recipes import post, orphaned_organization

grade = Recipe(
    Grade,
    code=seq("")
)

skill = Recipe(
    Skill,
    code=seq("")
)

position = Recipe(
    Position,
    grade=foreign_key('grade'),
    skill=foreign_key('skill'),
    post=foreign_key(post),
    bureau=foreign_key(orphaned_organization)
)


def bidcycle_positions(*args, **kwargs):
    pos = mommy.make(Position, *args, **kwargs)
    bidcycle = BidCycle.objects.first()
    if not bidcycle:
        bidcycle = mommy.make(BidCycle, active=True)
    if isinstance(pos, list):
        bidcycle.positions.add(*pos)
    else:
        bidcycle.positions.add(pos)
    return pos


def favorite_position():
    pos = mommy.make(Position)
    pos.classifications.add(mommy.make(Classification))
    up = UserProfile.objects.last()
    up.favorite_positions.add(pos)
    up.save()
    return pos


def highlighted_position():
    pos = mommy.make(Position)
    org = mommy.make("organization.Organization")
    org.highlighted_positions.add(pos)
    return pos


def assignment_for_user():
    assignment = mommy.make(Assignment, user=UserProfile.objects.last(), position=mommy.make(Position), tour_of_duty=mommy.make('organization.TourOfDuty', months=6))
    assignment.start_date = "2017-02-01T00:00:00Z"
    assignment.save()
    return assignment
