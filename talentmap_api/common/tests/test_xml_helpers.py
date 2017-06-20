import pytest
import os

from django.conf import settings
from django.core.management import call_command

from talentmap_api.language.models import Language, Proficiency


@pytest.mark.django_db()
def test_xml_language_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_languages.xml'),
                 'languages')

    assert Language.objects.count() == 2
    assert Language.objects.filter(long_description__contains="German").count() == 1
    assert Language.objects.filter(long_description__contains="French").count() == 1


@pytest.mark.django_db()
def test_xml_language_proficiency_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_language_proficiencies.xml'),
                 'proficiencies')

    assert Proficiency.objects.count() == 1
    assert Proficiency.objects.filter(code="0").count() == 1


@pytest.mark.django_db()
def test_xml_grades_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_grades.xml'),
                 'grades')

    assert Grade.objects.count() == 1
    assert Grade.objects.filter(code="00").count() == 1
