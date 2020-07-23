import pytest

from django.core.management import call_command

from talentmap_api.bidding.models import BidCycle, CyclePosition
from talentmap_api.language.models import Language
from talentmap_api.position.models import Grade, Skill, Position, SkillCone, CapsuleDescription
from talentmap_api.organization.models import Organization, TourOfDuty, Post, Location, Country
from talentmap_api.common.common_helpers import LANGUAGE_FORMAL_NAMES

from talentmap_api.integrations.models import SynchronizationJob, SynchronizationTask
from talentmap_api.integrations.management.commands.schedule_synchronization_job import Command as SyncCommand

from talentmap_api.common.common_helpers import ensure_date

from talentmap_api.position.tests.mommy_recipes import bidcycle_positions


@pytest.mark.django_db(transaction=True)
def test_soap_integrations():
    # Create the default synchronizations
    call_command('schedule_synchronization_job', '--set-defaults')
    call_command('synchronize_data', '--test')

    assert Language.objects.count() == 10
    assert Language.objects.first().formal_description == LANGUAGE_FORMAL_NAMES.get(Language.objects.first().short_description)
    assert Country.objects.count() == 10
    assert Location.objects.count() == 10
    assert CapsuleDescription.objects.count() == 10
    assert Post.objects.count() == 19  # 10 from the file, 9 from the positions
    assert TourOfDuty.objects.count() == 5
    assert Grade.objects.count() == 13
    assert Skill.objects.count() == 71
    assert SkillCone.objects.count() == 10
    assert Position.objects.count() == 10
    assert BidCycle.objects.first().active == False
    assert BidCycle.objects.first()._cycle_status == 'C'
    assert BidCycle.objects.get(_id="151").active == True

    # Assert is_overseas
    assert Position.objects.get(_seq_num="1640").is_overseas == True

    call_command('synchronize_data', '--list')

    first_skill = Skill.objects.first()
    first_skill.description = "Ring making"
    first_skill.save()
    first_skill.refresh_from_db()

    assert first_skill.description == "Ring making"

    call_command('schedule_synchronization_job', 'position.Skill', '--reset')
    call_command('synchronize_data', '--model', 'position.Skill', '--test')

    first_skill = Skill.objects.get(id=first_skill.id)
    assert not first_skill.description == "Ring making"

    call_command('schedule_synchronization_job', 'position.Skill', '10')

    assert SynchronizationJob.objects.get(talentmap_model='position.Skill').delta_synchronization == 10


@pytest.mark.django_db(transaction=True)
def test_soap_job_functions():
    call_command('schedule_synchronization_job', '--set-defaults')

    default_jobs = SyncCommand().default_jobs

    assert SynchronizationJob.objects.count() == len(default_jobs)

    call_command('schedule_synchronization_job', default_jobs[0][0], '--remove')

    assert SynchronizationJob.objects.count() == len(default_jobs) - 1

    call_command('schedule_synchronization_job', '--list')

    job = SynchronizationJob.objects.first()
    job.last_synchronization = "2011-01-01T00:00:00Z"
    job.save()

    call_command('schedule_synchronization_job', job.talentmap_model, '--reset')

    job.refresh_from_db()
    assert job.last_synchronization == ensure_date("1975-01-01T00:00:00Z")

    call_command('schedule_synchronization_job', job.talentmap_model, '1000', '0', '--use-last-updated true')

    job.refresh_from_db()
    assert job.use_last_date_updated

    job.last_synchronization = "2011-01-01T00:00:00Z"
    job.save()

    call_command('schedule_synchronization_job', '--reset-all')

    job.refresh_from_db()
    assert job.last_synchronization == ensure_date("1975-01-01T00:00:00Z")

    job.running = False
    job.save()

    call_command('schedule_synchronization_job', '--stop-running')

    job.refresh_from_db()
    assert job.running == False


@pytest.mark.django_db(transaction=True)
def test_soap_job_tasks():
    task = SynchronizationTask()
    task.talentmap_model = "position.Position"
    task.save()

    assert task.priority == 0


@pytest.mark.django_db(transaction=True)
def test_soap_bidcycle_active():
    call_command('schedule_synchronization_job', '--set-defaults')
    assert BidCycle.objects.count() == 0

    closing_bidcycle = BidCycle.objects.create(id=151, _id="151", name="Test Cycle", _cycle_status='P', active=False)
    closing_bidcycle.save()
    closing_bidcycle.refresh_from_db()

    bidcycle_positions(_quantity=5)

    assert BidCycle.objects.count() == 1

    assert BidCycle.objects.get(_id="151").active == False
    assert BidCycle.objects.get(_id="151")._cycle_status == 'P'

    call_command('schedule_synchronization_job', 'bidding.BidCycle', '--reset')
    call_command('synchronize_data', '--model', 'bidding.BidCycle', '--test')

    assert BidCycle.objects.get(_id="151").active == True
    assert BidCycle.objects.get(_id="151")._cycle_status == 'A'

    assert CyclePosition.objects.filter(bidcycle=closing_bidcycle).first().status == 'OP'
    assert CyclePosition.objects.filter(bidcycle=closing_bidcycle).first().status_code == 'OP'


@pytest.mark.django_db(transaction=True)
def test_soap_bidcycle_close():
    call_command('schedule_synchronization_job', '--set-defaults')
    assert BidCycle.objects.count() == 0

    closing_bidcycle = BidCycle.objects.create(id=138, _id="138", name="Test Cycle", _cycle_status='A', active=True)
    closing_bidcycle.save()
    closing_bidcycle.refresh_from_db()

    bidcycle_positions(_quantity=5)

    assert BidCycle.objects.count() == 1

    assert BidCycle.objects.get(_id="138").active == True
    assert BidCycle.objects.get(_id="138")._cycle_status == 'A'

    call_command('schedule_synchronization_job', 'bidding.BidCycle', '--reset')
    call_command('synchronize_data', '--model', 'bidding.BidCycle', '--test')

    assert BidCycle.objects.get(_id="138").active == False
    assert BidCycle.objects.get(_id="138")._cycle_status == 'C'

    assert CyclePosition.objects.filter(bidcycle=closing_bidcycle).first().status == 'MC'
    assert CyclePosition.objects.filter(bidcycle=closing_bidcycle).first().status_code == 'MC'
