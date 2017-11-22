import pytest
from dateutil.relativedelta import relativedelta

from talentmap_api.position.models import Position, Assignment
from talentmap_api.organization.models import TourOfDuty
from talentmap_api.user_profile.models import UserProfile

from model_mommy import mommy


@pytest.fixture
def test_assignment_fixture():
    mommy.make('organization.TourOfDuty', months=12)
    mommy.make_recipe('talentmap_api.position.tests.position')


@pytest.mark.django_db(transaction=True)
def test_assignment_position_update(authorized_client, authorized_user):
    position = mommy.make_recipe('talentmap_api.position.tests.position')
    position_2 = mommy.make_recipe('talentmap_api.position.tests.position')

    # Create an Assignment
    assignment = Assignment.objects.create(position=position, user=authorized_user.profile, tour_of_duty=mommy.make('organization.TourOfDuty'))
    position.refresh_from_db()
    assert position.current_assignment == assignment

    assignment.position = position_2
    assignment.save()
    position.refresh_from_db()
    assert position.current_assignment is None


@pytest.mark.django_db(transaction=True)
def test_assignment_estimated_end_date(authorized_client, authorized_user, test_assignment_fixture):
    # Get our required foreign key data
    user = UserProfile.objects.get(user=authorized_user)

    position = Position.objects.first()
    tour_of_duty = TourOfDuty.objects.filter(months=12).first()

    # Create an assignment
    assignment = Assignment.objects.create(user=user, position=position, tour_of_duty=tour_of_duty)

    # Assert the dates are currently null
    assert assignment.start_date is None
    assert assignment.estimated_end_date is None

    # Now save a start date
    assignment.start_date = "1991-02-01"
    assignment.save()
    assignment.refresh_from_db()

    expected_estimated_end_date = assignment.start_date + relativedelta(months=12)

    assert assignment.estimated_end_date == expected_estimated_end_date
