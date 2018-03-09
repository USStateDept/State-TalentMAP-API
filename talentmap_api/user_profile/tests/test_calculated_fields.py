import pytest
from freezegun import freeze_time

from model_mommy import mommy

from talentmap_api.position.models import Assignment

@pytest.mark.django_db()
def test_user_display_name():
    user_1 = mommy.make('auth.User', first_name="Johnny", last_name="State", email="StateJB@state.gov")
    user_2 = mommy.make('auth.User', username="statej", email="StateJB@state.gov")
    user_3 = mommy.make('auth.User', email="StateJB@state.gov")

    assert user_1.profile.display_name == "Johnny"
    assert user_2.profile.display_name == "statej"
    assert user_3.profile.display_name == "StateJB@state.gov"


@pytest.mark.django_db()
def test_user_initials():
    user_1 = mommy.make('auth.User', first_name="Johnny", last_name="State")
    user_2 = mommy.make('auth.User', first_name="", last_name="", email="StateJB@state.gov")

    assert user_1.profile.initials == "JS"
    assert user_2.profile.initials == "JS"


@pytest.mark.django_db()
def test_fairshare_differential_case():
    with freeze_time("1990-01-01T00:00:00Z") as frozen_time:
        user_1 = mommy.make('auth.User').profile
        user_2 = mommy.make('auth.User').profile

        dangerous_post = mommy.make('organization.Post', danger_pay=10, differential_rate=10, tour_of_duty=mommy.make('organization.TourOfDuty', months=24))
        position = mommy.make('position.Position', post=dangerous_post)

        # Assign our users to the post
        # User 1 will have a 20 month assignment, User 2 will have a 15 month assignment
        assignment_1 = mommy.make('position.Assignment', position=position, user=user_1, start_date="1991-01-01T00:00:00Z", end_date="1992-09-01T00:00:00Z")
        assignment_1.status = Assignment.Status.completed
        assignment_1.save()

        assignment_2 = mommy.make('position.Assignment', position=position, user=user_2, start_date="1991-01-01T00:00:00Z", end_date="1992-04-01T00:00:00Z")
        assignment_2.status = Assignment.Status.completed
        assignment_2.save()

        assert user_1.is_fairshare
        assert not user_2.is_fairshare

        # Now, we freeze time in the future and change the differential and danger pay rates of the post
        frozen_time.move_to("1995-01-14T12:00:01Z")

        dangerous_post.danger_pay = 0
        dangerous_post.differential_rate = 0
        dangerous_post.save()

        # Previous fairshare calculations should hold here
        assert user_1.is_fairshare
        assert not user_2.is_fairshare


@pytest.mark.django_db()
def test_fairshare_twelve_month_tod_case():
    with freeze_time("1990-01-01T00:00:00Z") as frozen_time:
        user_1 = mommy.make('auth.User').profile
        user_2 = mommy.make('auth.User').profile

        one_year_post = mommy.make('organization.Post', danger_pay=0, differential_rate=0, tour_of_duty=mommy.make('organization.TourOfDuty', months=12))
        position = mommy.make('position.Position', post=one_year_post)

        # Assign our users to the post
        # User 1 will have a 10 month assignment, User 2 will have a 5 month assignment
        assignment_1 = mommy.make('position.Assignment', position=position, user=user_1, start_date="1991-01-01T00:00:00Z", end_date="1991-11-01T00:00:00Z")
        assignment_1.status = Assignment.Status.completed
        assignment_1.save()

        assignment_2 = mommy.make('position.Assignment', position=position, user=user_2, start_date="1991-01-01T00:00:00Z", end_date="1991-06-01T00:00:00Z")
        assignment_2.status = Assignment.Status.completed
        assignment_2.save()

        assert user_1.is_fairshare
        assert not user_2.is_fairshare

        # Now, we freeze time in the future and change the base tour of duty for our post
        frozen_time.move_to("1995-01-14T12:00:01Z")

        one_year_post.tour_of_duty = mommy.make('organization.TourOfDuty', months=36)
        one_year_post.save()

        # Previous fairshare calculations should hold here
        assert user_1.is_fairshare
        assert not user_2.is_fairshare


@pytest.mark.django_db()
def test_cdo_flag():
    user_1 = mommy.make('auth.User').profile
    user_2 = mommy.make('auth.User').profile

    user_2.cdo = user_1
    user_2.save()
    user_2.refresh_from_db()

    assert user_1.is_cdo
    assert not user_2.is_cdo


@freeze_time("1991-10-12T00:00:00Z")
@pytest.mark.django_db()
def test_six_eight_cases():
    with freeze_time("1990-01-01T00:00:00Z") as frozen_time:
        user_1 = mommy.make('auth.User').profile

        domestic_post = mommy.make('organization.Post', location__country__code="USA", tour_of_duty=mommy.make('organization.TourOfDuty', months=24))
        foreign_post = mommy.make('organization.Post', location__country__code="DDR", tour_of_duty=mommy.make('organization.TourOfDuty', months=12))

        domestic_position = mommy.make('position.Position', post=domestic_post)
        foreign_position = mommy.make('position.Position', post=foreign_post, is_overseas=True)

        tod_case_1 = mommy.make('organization.TourOfDuty', months=12)
        tod_case_2 = mommy.make('organization.TourOfDuty', months=24)
        tod_case_3 = mommy.make('organization.TourOfDuty', months=36)
        tod_case_4 = mommy.make('organization.TourOfDuty', months=100)

        # Give our user six years of continuous domestic
        assignment_1 = mommy.make('position.Assignment', position=domestic_position, user=user_1, is_domestic=True, start_date="1991-01-01T00:00:00Z", end_date="1994-01-01T00:00:00Z", status="active")
        assignment_1.status = Assignment.Status.completed
        assignment_1.save()

        assignment_2 = mommy.make('position.Assignment', position=domestic_position, user=user_1, is_domestic=True, start_date="1994-01-01T00:00:00Z", end_date="1997-01-01T00:00:00Z", status="active")
        assignment_2.status = Assignment.Status.completed
        assignment_2.save()

        assert not user_1.is_six_eight

        # Give our user a small stint foreign, but not enough to trigger 6/8 validation
        tod_assignment = mommy.make('position.Assignment', position=foreign_position, user=user_1, tour_of_duty=tod_case_1, start_date="1997-01-02T00:00:00Z", end_date="1997-08-01T00:00:00Z", status="active")
        tod_assignment.status = Assignment.Status.completed
        tod_assignment.save()

        assert user_1.assignments.count() == 3
        assert not user_1.is_six_eight

        # Make that assignment sufficient length
        tod_assignment.end_date = "1998-01-02T00:00:00Z"
        tod_assignment.save()

        assert user_1.is_six_eight

        # Change the tour of duty to a longer one where this is no longer valid
        tod_assignment.tour_of_duty = tod_case_2
        tod_assignment.save()

        assert not user_1.is_six_eight

        # Make that assignment sufficient length
        tod_assignment.end_date = "1999-01-02T00:00:00Z"
        tod_assignment.save()

        assert user_1.is_six_eight

        # Change the tour of duty to a longer one where this is no longer valid
        tod_assignment.tour_of_duty = tod_case_3
        tod_assignment.save()

        assert not user_1.is_six_eight

        # Make that assignment sufficient length
        tod_assignment.end_date = "2000-01-02T00:00:00Z"
        tod_assignment.save()

        assert user_1.is_six_eight

        # Change the tour of duty to a longer one where this is no longer valid
        tod_assignment.tour_of_duty = tod_case_4
        tod_assignment.save()

        assert not user_1.is_six_eight

        # Make that assignment sufficient length
        tod_assignment.end_date = "2003-12-02T00:00:00Z"
        tod_assignment.save()

        assert user_1.is_six_eight

        frozen_time.move_to("2004-01-01T00:00:00Z")
        tod_assignment.position = domestic_position
        tod_assignment.save()

        # User should still be six eight as when they served it was a foreign position
        assert user_1.is_six_eight
