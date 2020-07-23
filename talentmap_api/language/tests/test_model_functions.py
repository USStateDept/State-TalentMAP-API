import pytest

from model_mommy import mommy

from talentmap_api.language.models import Language, Qualification
from talentmap_api.common.common_helpers import LANGUAGE_FORMAL_NAMES


@pytest.fixture
def test_language_model_fixture():
    # Create a specific language, and set of proficiency, and qualification
    mommy.make('language.Language', code="DE", long_description="German", short_description="Ger")
    mommy.make('language.Proficiency', code="3+")
    mommy.make('language.Proficiency', code="3")


@pytest.mark.django_db()
def test_model_save():
    lang = Language.objects.create(code="AD", short_description="Arabic-Mod")
    lang.save()

    assert lang.formal_description is not None
    assert lang.formal_description == LANGUAGE_FORMAL_NAMES.get("Arabic-Mod")

    lang.refresh_from_db()
    lang.short_description = "Serbo-Croa"
    lang.save()

    assert lang.formal_description is not None
    assert lang.formal_description == LANGUAGE_FORMAL_NAMES.get("Serbo-Croa")
    assert lang.formal_description == "Serbo-Croatian (Croatian)"


@pytest.mark.django_db()
def test_proficiency_comparisons():
    p1 = mommy.make('language.Proficiency', id=1, code='3+')
    p2 = p1
    p3 = mommy.make('language.Proficiency', id=2, code='X')
    p4 = mommy.make('language.Proficiency', id=3, code='2')

    assert p1 >= p2
    assert p1 <= p2
    assert p1 > p3
    assert p1 > p4
    assert p4 <= p2
    assert p4 > p3
    assert p3 < p4


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
