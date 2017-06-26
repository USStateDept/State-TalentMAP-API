import pytest
import os

from django.conf import settings
from django.core.management import call_command

from model_mommy import mommy

from talentmap_api.language.models import Language, Proficiency
from talentmap_api.position.models import Grade, Skill, Position
from talentmap_api.organization.models import Organization


@pytest.mark.django_db(transaction=True)
def test_xml_collision_noaction():
    mommy.make('position.Skill', code="0010", description="START DESCRIPTION")

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_collision_1.xml'),
                 'skills')

    assert Skill.objects.count() == 1
    assert Skill.objects.filter(description="START DESCRIPTION").count() == 1


@pytest.mark.django_db(transaction=True)
def test_xml_collision_delete():
    start = mommy.make('position.Skill', code="0010", description="START DESCRIPTION")
    start_id = start.id

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_collision_1.xml'),
                 'skills',
                 '--delete')

    assert Skill.objects.count() == 1
    assert Skill.objects.filter(description="NEW DESCRIPTION").count() == 1
    assert Skill.objects.first().id != start_id


@pytest.mark.django_db(transaction=True)
def test_xml_collision_update():
    start = mommy.make('position.Skill', code="0010", description="START DESCRIPTION")
    start_id = start.id

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_collision_1.xml'),
                 'skills',
                 '--update')

    assert Skill.objects.count() == 1
    assert Skill.objects.filter(description="NEW DESCRIPTION").count() == 1
    assert Skill.objects.first().id == start_id


@pytest.mark.django_db()
def test_xml_null_values():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_languages_nulls.xml'),
                 'languages')

    assert Language.objects.count() == 2
    assert Language.objects.filter(code="GM").count() == 1
    assert Language.objects.filter(code="FR").count() == 1


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


@pytest.mark.django_db()
def test_xml_skills_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_skills.xml'),
                 'skills')

    assert Skill.objects.count() == 1
    assert Skill.objects.filter(code="0010").count() == 1


@pytest.mark.django_db()
def test_xml_organizations_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_organizations.xml'),
                 'organizations')

    assert Organization.objects.count() == 4
    assert Organization.objects.filter(code="010101").count() == 1


@pytest.mark.django_db(transaction=True)
def test_xml_positions_loading():
    # Make the objects that this position will be linking to
    lang_2 = mommy.make('language.Language', code="DE")
    prof_1 = mommy.make('language.Proficiency', code="2")
    prof_2 = mommy.make('language.Proficiency', code="2+")

    org = mommy.make('organization.Organization', code="2345")
    bureau = mommy.make('organization.Organization', code="15")

    skill = mommy.make('position.Skill', code="9017")
    grade = mommy.make('position.Grade', code="05")

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_positions.xml'),
                 'positions')

    assert Position.objects.count() == 2
    position = Position.objects.first()

    assert position.organization == org
    assert position.bureau == bureau

    assert position.skill == skill
    assert position.grade == grade
