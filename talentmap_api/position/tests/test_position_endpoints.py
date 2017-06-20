import pytest

from model_mommy import mommy
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

    # Create a position with the specific qualification
    mommy.make('position.Position', language_requirements=[qualification])
    mommy.make('position.Position', language_requirements=[qualification_2])

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
