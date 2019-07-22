import pytest

from model_mommy import mommy
from rest_framework import status

from itertools import cycle

from django.contrib.auth.models import User
from django.utils import timezone
from talentmap_api.common.common_helpers import get_permission_by_name
from talentmap_api.position.tests.mommy_recipes import bidcycle_positions


# Might move this fixture to a session fixture if we end up needing languages elsewhere
@pytest.fixture
def test_position_endpoints_fixture():
    # Create a specific language, proficiency, and qualification
    language = mommy.make('language.Language', code="DE", long_description="German", short_description="Ger")
    mommy.make('language.Language', code="FR", long_description="French", short_description="Fch")
    proficiency = mommy.make('language.Proficiency', code="3")
    proficiency_2 = mommy.make('language.Proficiency', code="4")
    qualification = mommy.make('language.Qualification', language=language, spoken_proficiency=proficiency, reading_proficiency=proficiency)
    qualification_2 = mommy.make('language.Qualification', language=language, spoken_proficiency=proficiency_2, reading_proficiency=proficiency_2)

    # Create some grades
    grade = mommy.make('position.Grade', code="00")
    grade_2 = mommy.make('position.Grade', code="01")
    mommy.make_recipe('talentmap_api.position.tests.grade', _quantity=8)

    # Create some skills
    skill = mommy.make('position.Skill', code="0010")
    skill_2 = mommy.make('position.Skill', code="0020")
    mommy.make_recipe('talentmap_api.position.tests.skill', _quantity=8)

    bc = mommy.make('bidding.BidCycle', active=True)
    # Create a position with the specific qualification
    bc.positions.add(mommy.make('position.Position', languages=[qualification], grade=grade, skill=skill))
    bc.positions.add(mommy.make('position.Position', languages=[qualification_2], grade=grade_2, skill=skill_2))

    is_overseas = [True, False]
    # Create some junk positions to add numbers
    for _ in range(0, 8):
        bc.positions.add(mommy.make('position.Position',
                                    organization=mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization'),
                                    bureau=mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization'),
                                    is_overseas=cycle(is_overseas)))


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_position_list(client):
    response = client.get('/api/v1/position/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_position_filtering(client):
    response = client.get('/api/v1/position/?languages__language__name=German')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = client.get('/api/v1/position/?language_codes=DE')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_least=3')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_most=3')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_least=4')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_most=4')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_position_grade_skill_filters(client):
    response = client.get('/api/v1/position/?grade__code=00')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = client.get('/api/v1/position/?skill__code=0010')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_grade_list(client):
    response = client.get('/api/v1/grade/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_grade_filtering(client):
    response = client.get('/api/v1/grade/?code=00')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = client.get('/api/v1/grade/?code__in=00,01')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_skill_list(client):
    response = client.get('/api/v1/skill/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_skill_filtering(client):
    response = client.get('/api/v1/skill/?code=0010')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = client.get('/api/v1/skill/?code__in=0010,0020')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
@pytest.mark.parametrize("endpoint, available, expected_count", [
    ("/api/v1/language/", True, 1),
    ("/api/v1/language/", False, 1),
    ("/api/v1/language_proficiency/", True, 2),
    ("/api/v1/language_proficiency/", False, 0),
    ("/api/v1/grade/", True, 2),
    ("/api/v1/grade/", False, 8),
    ("/api/v1/skill/", True, 2),
    ("/api/v1/skill/", False, 8),
])
def test_available_filtering(client, endpoint, available, expected_count):
    response = client.get(f'{endpoint}?is_available={available}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == expected_count


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_domestic_filtering(client):
    response_1 = client.get('/api/v1/position/?is_domestic=true')
    response_2 = client.get('/api/v1/position/?is_overseas=false')

    assert response_1.data == response_2.data

    response_1 = client.get('/api/v1/position/?is_domestic=false')
    response_2 = client.get('/api/v1/position/?is_overseas=true')

    assert response_1.data == response_2.data


@pytest.mark.django_db()
def test_position_assignment_list(authorized_client, authorized_user):
    # Give the user AO permissions
    group = mommy.make("auth.Group", name="bureau_ao")
    group.user_set.add(authorized_user)
    position = mommy.make("position.Position")
    mommy.make("position.Assignment", position=position, user=authorized_user.profile, tour_of_duty=mommy.make("organization.TourOfDuty"), _quantity=5)

    response = authorized_client.get(f'/api/v1/position/{position.id}/assignments/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5

@pytest.mark.django_db(transaction=True)
def test_highlight_action_endpoints(authorized_client, authorized_user):
    bureau = mommy.make('organization.Organization', code="123456", short_description="Test Bureau")
    bureau.create_permissions()
    permission = get_permission_by_name(f"organization.can_highlight_positions:{bureau.code}")

    position = bidcycle_positions(bureau=bureau)

    response = authorized_client.get(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # First, try to highlight without appropriate permissions
    response = authorized_client.put(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Now, try to unhiglight without appropriate permissions
    response = authorized_client.delete(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Add the permission to our user
    authorized_user.user_permissions.add(permission)
    group = mommy.make('auth.Group', name='superuser')
    group.user_set.add(authorized_user)

    response = authorized_client.put(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.delete(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
def test_position_waiver_actions(authorized_client, authorized_user):
    # Create a bureau for the position
    bureau = mommy.make('organization.Organization', code='12345')
    position = bidcycle_positions(bureau=bureau)
    bidcycle = mommy.make('bidding.BidCycle', active=True)
    cp = mommy.make('bidding.CyclePosition', position=position, bidcycle=bidcycle)
    bid = mommy.make('bidding.Bid', user=authorized_user.profile, position=cp, bidcycle=bidcycle)
    waiver = mommy.make('bidding.Waiver', user=authorized_user.profile, position=position, bid=bid)

    # Create valid permissions to view this position's waivers
    group = mommy.make('auth.Group', name='bureau_ao')
    group.user_set.add(authorized_user)
    group = mommy.make('auth.Group', name=f'bureau_ao:{bureau.code}')
    group.user_set.add(authorized_user)

    assert waiver.status == waiver.Status.requested

    # Pull a list of all the waivers
    response = authorized_client.get(f'/api/v1/position/{position.id}/waivers/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    # Approve the waiver
    response = authorized_client.get(f'/api/v1/position/{position.id}/waivers/{waiver.id}/approve/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    waiver.refresh_from_db()
    assert waiver.status == waiver.Status.approved
    assert waiver.reviewer == authorized_user.profile

    # Deny it the waiver
    response = authorized_client.get(f'/api/v1/position/{position.id}/waivers/{waiver.id}/deny/')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    waiver.refresh_from_db()
    assert waiver.status == waiver.Status.denied
    assert waiver.reviewer == authorized_user.profile


@pytest.mark.django_db(transaction=True)
def test_position_vacancy_filter_aliases(authorized_client, authorized_user):
    one_year_tod = mommy.make('organization.TourOfDuty', months=12)
    two_year_tod = mommy.make('organization.TourOfDuty', months=24)
    three_year_tod = mommy.make('organization.TourOfDuty', months=36)

    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    mommy.make('position.Assignment', position=bidcycle_positions(), start_date=today, tour_of_duty=one_year_tod, user=authorized_user.profile)
    mommy.make('position.Assignment', position=bidcycle_positions(), start_date=today, tour_of_duty=two_year_tod, user=authorized_user.profile)
    mommy.make('position.Assignment', position=bidcycle_positions(), start_date=today, tour_of_duty=three_year_tod, user=authorized_user.profile)

    response = authorized_client.get('/api/v1/position/?vacancy_in_years=1')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

    response = authorized_client.get('/api/v1/position/?vacancy_in_years=2')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = authorized_client.get('/api/v1/position/?vacancy_in_years=3')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3


@pytest.mark.django_db(transaction=True)
def test_position_similar_list(client):
    post = mommy.make_recipe('talentmap_api.organization.tests.post')
    skill = mommy.make('position.Skill')
    grade = mommy.make('position.Grade')
    position = bidcycle_positions(post=post, skill=skill, grade=grade)

    bidcycle_positions(post=post, skill=skill, grade=grade, _quantity=3)
    bidcycle_positions(post=mommy.make_recipe('talentmap_api.organization.tests.post'), skill=skill, grade=grade, _quantity=3)
    bidcycle_positions(post=mommy.make_recipe('talentmap_api.organization.tests.post'), skill=mommy.make('position.Skill'), grade=grade, _quantity=3)

    response = client.get(f'/api/v1/position/{position.id}/similar/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 3

    position.post = None
    position.save()
    position.refresh_from_db()

    response = client.get(f'/api/v1/position/{position.id}/similar/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 6

    position.skill = None
    position.save()
    position.refresh_from_db()

    response = client.get(f'/api/v1/position/{position.id}/similar/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 9