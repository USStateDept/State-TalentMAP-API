import pytest

from django.core.management import call_command

from talentmap_api.bidding.models import BidCycle, BiddingStatus
from talentmap_api.language.models import Language
from talentmap_api.position.models import Grade, Skill, Position, SkillCone, CapsuleDescription
from talentmap_api.organization.models import Organization, TourOfDuty, Post, Location, Country
from talentmap_api.common.common_helpers import LANGUAGE_FORMAL_NAMES

from talentmap_api.integrations.models import SynchronizationJob
from talentmap_api.integrations.management.commands.schedule_synchronization_job import Command as SyncCommand

from talentmap_api.common.common_helpers import ensure_date


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
    assert BidCycle.objects.count() == 8
    assert BidCycle.objects.get(_id="147").positions.count() == 4
    assert BidCycle.objects.get(_id="151").positions.count() == 6
    assert BiddingStatus.objects.count() == 10

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
