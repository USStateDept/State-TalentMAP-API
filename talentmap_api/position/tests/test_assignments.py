import pytest
import datetime
from freezegun import freeze_time

from talentmap_api.position.models import Position, Assignment
from talentmap_api.organization.models import TourOfDuty
from talentmap_api.user_profile.models import UserProfile

from model_mommy import mommy


@pytest.fixture
def test_assignment_fixture():
    mommy.make('organization.TourOfDuty', months=12)
    mommy.make_recipe('talentmap_api.position.tests.position')


@freeze_time("1991-02-01")
@pytest.mark.django_db(transaction=True)
def test_assignment_estimated_end_date(authorized_client, authorized_user, test_assignment_fixture):
    # Get our required foreign key data
    user = UserProfile.objects.get(user=authorized_user)
    position = Position.objects.first()
    tour_of_duty = TourOfDuty.objects.first()

    # Create an assignment
    assignment = Assignment.objects.create(user=user, position=position, tour_of_duty=tour_of_duty)

    # Assert the dates are currently null
    assert assignment.start_date is None
    assert assignment.estimated_end_date is None

    # Now save a start date
    assignment.start_date = "1991-02-01"
    assignment.save()
    assignment.refresh_from_db()

    assert assignment.estimated_end_date == datetime.datetime.strptime('1992-02-01', '%Y-%m-%d').date()
