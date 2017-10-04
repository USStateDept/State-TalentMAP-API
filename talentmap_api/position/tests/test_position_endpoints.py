import pytest

from model_mommy import mommy
from rest_framework import status

from itertools import cycle

from django.contrib.auth.models import User
from talentmap_api.common.common_helpers import get_permission_by_name


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

    # Create a position with the specific qualification
    mommy.make('position.Position', language_requirements=[qualification], grade=grade, skill=skill)
    mommy.make('position.Position', language_requirements=[qualification_2], grade=grade_2, skill=skill_2)

    is_overseas = [True, False]
    # Create some junk positions to add numbers
    mommy.make('position.Position',
               organization=mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization'),
               bureau=mommy.make_recipe('talentmap_api.organization.tests.orphaned_organization'),
               is_overseas=cycle(is_overseas),
               _quantity=8)


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
def test_favorite_action_endpoints(authorized_client, authorized_user):
    position = mommy.make_recipe('talentmap_api.position.tests.position')
    response = authorized_client.get(f'/api/v1/position/{position.id}/favorite/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = authorized_client.put(f'/api/v1/position/{position.id}/favorite/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/position/{position.id}/favorite/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.delete(f'/api/v1/position/{position.id}/favorite/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/position/{position.id}/favorite/')

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
def test_highlight_action_endpoints(authorized_client, authorized_user):
    bureau = mommy.make('organization.Organization', code="123456", short_description="Test Bureau")
    bureau.create_permissions()
    permission = get_permission_by_name(f"organization.can_highlight_positions_{bureau.code}")

    position = mommy.make_recipe('talentmap_api.position.tests.position', bureau=bureau)

    response = authorized_client.get(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_404_NOT_FOUND

    # First, try to highlight without appropriate permissions
    assert not authorized_user.has_perm(f"{permission.content_type.app_label}.{permission.codename}")
    response = authorized_client.put(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Now, try to unhiglight without appropriate permissions
    response = authorized_client.delete(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Add the permission to our user
    authorized_user.user_permissions.add(permission)
    # Must re-acquire the user from the DB after adding permissions due to caching
    authorized_user = User.objects.get(id=authorized_user.id)
    assert authorized_user.has_perm(f"{permission.content_type.app_label}.{permission.codename}")

    response = authorized_client.put(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.delete(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    response = authorized_client.get(f'/api/v1/position/{position.id}/highlight/')

    assert response.status_code == status.HTTP_404_NOT_FOUND
