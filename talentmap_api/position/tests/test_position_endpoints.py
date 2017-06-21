import pytest

from model_mommy import mommy
from model_mommy.recipe import Recipe, seq
from rest_framework import status


# Might move this fixture to a session fixture if we end up needing languages elsewhere
@pytest.fixture
def test_position_endpoints_fixture():
    # Create a specific language, proficiency, and qualification
    language = mommy.make('language.Language', code="DE", long_description="German", short_description="Ger")
    proficiency = mommy.make('language.Proficiency', code="3")
    proficiency_2 = mommy.make('language.Proficiency', code="4")
    qualification = mommy.make('language.Qualification', language=language, spoken_proficiency=proficiency, written_proficiency=proficiency)
    qualification_2 = mommy.make('language.Qualification', language=language, spoken_proficiency=proficiency_2, written_proficiency=proficiency_2)

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

    # Create some junk positions to add numbers
    mommy.make('position.Position', _quantity=8)


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_position_list(client):
    response = client.get('/api/v1/position/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_position_filtering(client):
    response = client.get('/api/v1/position/?languages__language__name=German')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_least=3')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_most=3')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_least=4')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    response = client.get('/api/v1/position/?languages__spoken_proficiency__at_most=4')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_grade_list(client):
    response = client.get('/api/v1/position/grades/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_grade_filtering(client):
    response = client.get('/api/v1/position/grades/?code=00')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    response = client.get('/api/v1/position/grades/?code__in=00,01')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_skill_list(client):
    response = client.get('/api/v1/position/skills/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_position_endpoints_fixture")
def test_skill_filtering(client):
    response = client.get('/api/v1/position/skills/?code=0010')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

    response = client.get('/api/v1/position/skills/?code__in=0010,0020')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
