import pytest

from model_mommy import mommy

from talentmap_api.language.models import Qualification


@pytest.fixture
def test_language_model_fixture():
    # Create a specific language, and set of proficiency, and qualification
    mommy.make('language.Language', code="DE", long_description="German", short_description="Ger")
    mommy.make('language.Proficiency', code="3+")
    mommy.make('language.Proficiency', code="3")


@pytest.mark.django_db()
@pytest.mark.usefixtures("test_language_model_fixture")
def test_qualification_get_or_create_by_codes():
    qual, created = Qualification.get_or_create_by_codes("DE", "3+", "3")

    assert created
    assert qual.language.code == "DE"
    assert qual.reading_proficiency.code == "3+"
    assert qual.spoken_proficiency.code == "3"

    qual, created = Qualification.get_or_create_by_codes("DE", "3+", "3")

    assert not created
    assert qual.language.code == "DE"
    assert qual.reading_proficiency.code == "3+"
    assert qual.spoken_proficiency.code == "3"
