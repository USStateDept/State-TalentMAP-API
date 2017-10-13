import pytest
import os

from django.conf import settings
from django.core.management import call_command

from model_mommy import mommy

from talentmap_api.language.models import Language, Proficiency
from talentmap_api.position.models import Grade, Skill, Position, CapsuleDescription
from talentmap_api.organization.models import Organization, TourOfDuty, Post, Location, Country


@pytest.mark.django_db(transaction=True)
def test_xml_collision_noaction():
    mommy.make('position.Skill', code="0010", description="START DESCRIPTION")

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_collision_1.xml'),
                 'skills')

    assert Skill.objects.count() == 1
    assert Skill.objects.filter(description="START DESCRIPTION").count() == 1


@pytest.mark.django_db(transaction=True)
def test_xml_collision_noaction_multiples():
    mommy.make('position.Position', _seq_num="111", _quantity=3)

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_positions.xml'),
                 'positions')

    assert Position.objects.filter(_seq_num="111").count() == 3


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
    assert Grade.objects.filter(code="00").first().rank == Grade.RANK_ORDERING.get("00")


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
    assert Organization.objects.filter(code="010000").first().is_bureau


@pytest.mark.django_db(transaction=True)
def test_xml_regional_organizations_loading():
    mommy.make('organization.Location', code="110010001")

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_organizations.xml'),
                 'organizations')

    assert Organization.objects.count() == 4
    assert Organization.objects.filter(code="110000").count() == 1
    assert Organization.objects.get(code="110000").is_regional


@pytest.mark.django_db()
def test_xml_tour_of_duty_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_tour_of_duty.xml'),
                 'tours_of_duty')

    assert TourOfDuty.objects.count() == 3
    assert TourOfDuty.objects.filter(code="2").count() == 1


@pytest.mark.django_db(transaction=True)
def test_xml_post_loading():
    tod_1 = mommy.make('organization.TourOfDuty', code="I")
    tod_2 = mommy.make('organization.TourOfDuty', code="O")

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_bidding_tool_posts.xml'),
                 'posts')

    assert Post.objects.count() == 2
    assert Post.objects.filter(_location_code="AF1000000").count() == 1
    assert Post.objects.filter(_location_code="AF1000000").first().tour_of_duty == tod_2
    assert Post.objects.filter(_location_code="AE1200000").first().tour_of_duty == tod_1


@pytest.mark.django_db(transaction=True)
def test_xml_positions_loading():
    # Make the objects that this position will be linking to
    mommy.make('language.Language', code="DE")
    mommy.make('language.Proficiency', code="2")
    mommy.make('language.Proficiency', code="2+")

    org = mommy.make('organization.Organization', code="2345")
    bureau = mommy.make('organization.Organization', code="15")

    skill = mommy.make('position.Skill', code="9017")
    grade = mommy.make('position.Grade', code="05")

    location = mommy.make('organization.Location', code="SL2000000")
    post = mommy.make('organization.Post', location=location, _location_code=location.code)

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_positions.xml'),
                 'positions')

    assert Position.objects.count() == 2
    position = Position.objects.first()

    assert position.organization == org
    assert position.bureau == bureau

    assert position.skill == skill
    assert position.grade == grade

    assert position.post == post


@pytest.mark.django_db()
def test_xml_country_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_countries.xml'),
                 'countries')

    assert Country.objects.count() == 5
    country = Country.objects.get(code="AND")
    assert country.short_code == "AD"
    assert country.location_prefix == "AN"
    assert country.name == "Principality of Andorra"
    assert country.short_name == "Andorra"


@pytest.mark.django_db()
def test_xml_location_loading():
    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_locations.xml'),
                 'locations')

    mommy.make('organization.Country', id=1, code="USA")
    mommy.make('organization.Country', id=2, location_prefix="VM")

    call_command('update_relationships')
    assert Location.objects.count() == 4
    assert Location.objects.filter(code="VM3000000").first().country.id == 2
    assert Location.objects.filter(code="063260073").first().country.id == 1


@pytest.mark.django_db()
def test_xml_capsule_description_loading():
    mommy.make("position.Position", _seq_num=1)
    mommy.make("position.Position", _seq_num=2)

    call_command('load_xml',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_capsule_description.xml'),
                 'capsule_descriptions')

    call_command('update_relationships')

    assert CapsuleDescription.objects.count() == 2
    assert Position.objects.get(_seq_num=1).description._pos_seq_num == '1'
    assert Position.objects.get(_seq_num=2).description._pos_seq_num == '2'
