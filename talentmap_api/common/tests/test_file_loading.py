import pytest
import os

from django.conf import settings
from django.core.management import call_command

from model_mommy import mommy

from talentmap_api.glossary.models import GlossaryEntry


@pytest.mark.django_db(transaction=True)
def test_csv_collision_noaction():
    GlossaryEntry.objects.create(title="item1", link="link1", definition="")

    call_command('load_csv',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_glossary.csv'),
                 'glossary')

    assert GlossaryEntry.objects.count() == 3

    item1 = GlossaryEntry.objects.get(title="item1")

    assert item1.definition == ""
    assert item1.link == "link1"


@pytest.mark.django_db(transaction=True)
def test_csv_collision_delete():
    start = GlossaryEntry.objects.create(title="item1", link="link1", definition="")
    start_id = start.id

    call_command('load_csv',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_glossary.csv'),
                 'glossary',
                 '--delete')

    assert GlossaryEntry.objects.count() == 3

    item1 = GlossaryEntry.objects.get(title="item1")

    assert item1.id != start_id
    assert item1.link == ""


@pytest.mark.django_db(transaction=True)
def test_csv_collision_update():
    start = GlossaryEntry.objects.create(title="item1", link="link1", definition="")

    start_id = start.id

    call_command('load_csv',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_glossary.csv'),
                 'glossary',
                 '--update')

    assert GlossaryEntry.objects.count() == 3

    item1 = GlossaryEntry.objects.get(title="item1")

    assert item1.id == start_id
    assert item1.link == ""
    assert item1.definition == "def1"


@pytest.mark.django_db()
def test_csv_glossary_loading():
    call_command('load_csv',
                 os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'test_glossary.csv'),
                 'glossary')

    assert GlossaryEntry.objects.count() == 3

    item1 = GlossaryEntry.objects.get(title="item1")
    item2 = GlossaryEntry.objects.get(title="item2")
    item3 = GlossaryEntry.objects.get(title="item3")

    assert item1.definition == "def1"
    assert item2.definition == "def2"
    assert item3.definition == "def3"

    assert item1.link == ""
    assert item2.link == "link2"
    assert item3.link == "link3"
