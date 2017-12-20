import pytest

from model_mommy import mommy


@pytest.mark.django_db()
def test_fairshare_differential_case():
    user_1 = mommy.make('auth.User').profile
    user_2 = mommy.make('auth.User').profile

    dangerous_post = mommy.make('organization.Post', danger_pay=10, differential_rate=10, tour_of_duty=mommy.make('organization.TourOfDuty', months=24))
    position = mommy.make('position.Position', post=dangerous_post)

    # Assign our users to the post
    # User 1 will have a 20 month assignment, User 2 will have a 15 month assignment
    mommy.make('position.Assignment', position=position, user=user_1, start_date="1991-01-01", end_date="1992-09-01")
    mommy.make('position.Assignment', position=position, user=user_2, start_date="1991-01-01", end_date="1992-04-01")

    assert user_1.is_fairshare
    assert not user_2.is_fairshare


@pytest.mark.django_db()
def test_fairshare_twelve_month_tod_case():
    user_1 = mommy.make('auth.User').profile
    user_2 = mommy.make('auth.User').profile

    one_year_post = mommy.make('organization.Post', danger_pay=0, differential_rate=0, tour_of_duty=mommy.make('organization.TourOfDuty', months=12))
    position = mommy.make('position.Position', post=one_year_post)

    # Assign our users to the post
    # User 1 will have a 10 month assignment, User 2 will have a 5 month assignment
    mommy.make('position.Assignment', position=position, user=user_1, start_date="1991-01-01", end_date="1991-11-01")
    mommy.make('position.Assignment', position=position, user=user_2, start_date="1991-01-01", end_date="1991-06-01")

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


@pytest.mark.django_db()
def test_six_eight_cases():
    user_1 = mommy.make('auth.User').profile

    domestic_position = mommy.make('position.Position', post__location__country__code="USA")
    foreign_position = mommy.make('position.Position', post__location__country__code="DDR")

    tod_case_1 = mommy.make('organization.TourOfDuty', months=12)
    tod_case_2 = mommy.make('organization.TourOfDuty', months=24)
    tod_case_3 = mommy.make('organization.TourOfDuty', months=36)
    tod_case_4 = mommy.make('organization.TourOfDuty', months=100)

    # Give our user six years of continuous domestic
    mommy.make('position.Assignment', position=domestic_position, user=user_1, start_date="1991-01-01", end_date="1994-01-01", status="completed")
    mommy.make('position.Assignment', position=domestic_position, user=user_1, start_date="1994-01-01", end_date="1997-01-01", status="completed")

    assert not user_1.is_six_eight

    # Give our user a small stint foreign, but not enough to trigger 6/8 validation
    tod_assignment = mommy.make('position.Assignment', position=foreign_position, user=user_1, tour_of_duty=tod_case_1, start_date="1997-01-02", end_date="1997-08-01", status="completed")

    assert user_1.assignments.count() == 3
    assert not user_1.is_six_eight

    # Make that assignment sufficient length
    tod_assignment.end_date = "1998-01-02"
    tod_assignment.save()

    assert user_1.is_six_eight

    # Change the tour of duty to a longer one where this is no longer valid
    tod_assignment.tour_of_duty = tod_case_2
    tod_assignment.save()

    assert not user_1.is_six_eight

    # Make that assignment sufficient length
    tod_assignment.end_date = "1999-01-02"
    tod_assignment.save()

    assert user_1.is_six_eight

    # Change the tour of duty to a longer one where this is no longer valid
    tod_assignment.tour_of_duty = tod_case_3
    tod_assignment.save()

    assert not user_1.is_six_eight

    # Make that assignment sufficient length
    tod_assignment.end_date = "2000-01-02"
    tod_assignment.save()

    assert user_1.is_six_eight

    # Change the tour of duty to a longer one where this is no longer valid
    tod_assignment.tour_of_duty = tod_case_4
    tod_assignment.save()

    assert not user_1.is_six_eight

    # Make that assignment sufficient length
    tod_assignment.end_date = "2003-12-02"
    tod_assignment.save()

    assert user_1.is_six_eight
