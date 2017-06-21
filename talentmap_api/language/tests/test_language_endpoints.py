import pytest

from model_mommy import mommy
from rest_framework import status


# Might move this fixture to a session fixture if we end up needing languages elsewhere
@pytest.fixture
def test_language_endpoints_fixture():
    # Create a bunch of languages where we don't care about the structure
    mommy.make_recipe('talentmap_api.language.tests.language', _quantity=9)
    mommy.make_recipe('talentmap_api.language.tests.proficiency', _quantity=9)

    # Create a specific language, proficiency, and qualification
    language = mommy.make('language.Language', code="DE", long_description="German", short_description="Ger")
    proficiency = mommy.make('language.Proficiency', code="3+")
    qualification = mommy.make('language.Qualification', language=language, spoken_proficiency=proficiency, written_proficiency=proficiency)


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_list(client):
    response = client.get('/api/v1/language/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_proficiency_list(client):
    response = client.get('/api/v1/language/proficiencies/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_qualification_list(client):
    response = client.get('/api/v1/language/qualifications/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["language"] == "German (DE)"
    assert response.data[0]["spoken_proficiency"] == "3+"
    assert response.data[0]["written_proficiency"] == "3+"
