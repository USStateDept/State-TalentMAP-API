import pytest
import json

from model_mommy import mommy
from rest_framework import status

from talentmap_api.language.models import Qualification


# Might move this fixture to a session fixture if we end up needing languages elsewhere
@pytest.fixture
def test_language_endpoints_fixture():
    mommy.make('language.Language', code="FR", id=1)
    # Create a specific language, proficiency, and qualification
    language = mommy.make('language.Language', code="DE", long_description="German", short_description="Ger")
    proficiency = mommy.make('language.Proficiency', id=1, code="3+")

    # Create a bunch of languages where we don't care about the structure
    mommy.make_recipe('talentmap_api.language.tests.language', _quantity=8)
    mommy.make_recipe('talentmap_api.language.tests.proficiency', _quantity=9)

    qualification = mommy.make('language.Qualification', language=language, spoken_proficiency=proficiency, written_proficiency=proficiency)


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_list(client):
    response = client.get('/api/v1/language/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_proficiency_list(client):
    response = client.get('/api/v1/language_proficiency/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 10


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_qualification_list(client):
    response = client.get('/api/v1/language_qualification/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["language"] == "German (DE)"
    assert response.data["results"][0]["spoken_proficiency"] == "3+"
    assert response.data["results"][0]["written_proficiency"] == "3+"


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_endpoints_fixture")
def test_language_qualification_creation(authorized_user, authorized_client):
    resp = authorized_client.put('/api/v1/language_qualification/', data=json.dumps({
        "language": 1,
        "written_proficiency": 1,
        "spoken_proficiency": 1
    }), content_type="application/json")

    assert resp.status_code == status.HTTP_201_CREATED
    assert Qualification.objects.filter(language_id=1, written_proficiency_id=1, spoken_proficiency_id=1).count() == 1
