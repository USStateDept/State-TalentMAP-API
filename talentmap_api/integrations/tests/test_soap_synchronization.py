import pytest

from django.core.management import call_command

from talentmap_api.language.models import Language
from talentmap_api.position.models import Grade, Skill, Position, SkillCone
from talentmap_api.organization.models import Organization, TourOfDuty, Post, Location, Country

from talentmap_api.integrations.models import SynchronizationJob
from talentmap_api.integrations.management.commands.schedule_synchronization_job import Command as SyncCommand

from talentmap_api.common.common_helpers import ensure_date


@pytest.mark.django_db(transaction=True)
def test_soap_integrations():
    # Create the default synchronizations
    call_command('schedule_synchronization_job', '--set-defaults')
    call_command('synchronize_data', '--test')

    assert Language.objects.count() == 10
    assert Country.objects.count() == 10
    assert Location.objects.count() == 10
    assert Organization.objects.count() == 20
    assert Post.objects.count() == 17  # 10 from the file, 7 from the positions
    assert TourOfDuty.objects.count() == 5
    assert Grade.objects.count() == 13
    assert Skill.objects.count() == 71
    assert SkillCone.objects.count() == 2
    assert Position.objects.count() == 10

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

    job.last_synchronization = "2011-01-01T00:00:00Z"
    job.save()

    call_command('schedule_synchronization_job', '--reset-all')

    job.refresh_from_db()
    assert job.last_synchronization == ensure_date("1975-01-01T00:00:00Z")
