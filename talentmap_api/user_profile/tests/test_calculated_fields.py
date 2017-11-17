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

    assert not user_1.is_fairshare
    assert user_2.is_fairshare


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

    assert not user_1.is_fairshare
    assert user_2.is_fairshare


@pytest.mark.django_db()
def test_cdo_flag():
    user_1 = mommy.make('auth.User').profile
    user_2 = mommy.make('auth.User').profile

    user_2.cdo = user_1
    user_2.save()
    user_2.refresh_from_db()

    assert user_1.is_cdo
    assert not user_2.is_cdo
