from django.core.management.base import BaseCommand

import logging

from talentmap_api.integrations.models import SynchronizationJob


class Command(BaseCommand):
    help = 'Creates and updates synchronization jobs'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Jobs, as a (model, delta) keypair
        self.default_jobs = [
            ('position.Skill', SynchronizationJob.TIME_WEEK, 0),
            ('position.Grade', SynchronizationJob.TIME_WEEK, 0),
            ('position.SkillCone', SynchronizationJob.TIME_WEEK, 0),
            ('position.CapsuleDescription', SynchronizationJob.TIME_DAY, 10),
            ('organization.TourOfDuty', SynchronizationJob.TIME_WEEK, 0),
            ('organization.Organization', SynchronizationJob.TIME_WEEK, 0),
            ('organization.Country', SynchronizationJob.TIME_WEEK, 0),
            ('organization.Location', SynchronizationJob.TIME_WEEK, 0),
            ('organization.Post', SynchronizationJob.TIME_WEEK, 0),
            ('language.Language', SynchronizationJob.TIME_WEEK, 0),
            ('position.Position', SynchronizationJob.TIME_DAY, 0),
            ('bidding.BidCycle', SynchronizationJob.TIME_HOUR, 1),
        ]

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='?', type=str, help="The model to schedule")
        parser.add_argument('delta', nargs='?', type=int, help="The delta synchronization in seconds")
        parser.add_argument('priority', nargs='?', type=int, help="The run priority of the job (0 is first)")
        parser.add_argument('--list', dest='list', action='store_true', help='Lists all synchronization jobs')
        parser.add_argument('--remove', dest='remove', action='store_true', help='Removes the specified model')
        parser.add_argument('--reset', dest='reset', action='store_true', help='Resets the last synchronization date on the model')
        parser.add_argument('--reset-all', dest='reset-all', action='store_true', help='Resets the last synchronization date on all models')
        parser.add_argument('--set-defaults', dest='set-defaults', action='store_true', help='Creates any missing baseline synchronization jobs')

    def handle(self, *args, **options):
        if options['list']:
            self.list_jobs()
            return

        if options['set-defaults']:
            self.set_defaults()
            return

        if options['reset-all']:
            SynchronizationJob.objects.update(last_synchronization="1975-01-01T00:00:00Z", running=False)
            return

        job, _ = SynchronizationJob.objects.get_or_create(talentmap_model=options['model'])

        self.logger.info(f"Old: {job}")

        if options['reset']:
            self.logger.info(f"Resetting: {job}")
            job.last_synchronization = "1975-01-01T00:00:00Z"
            job.save()
            return

        if options['remove']:
            self.logger.info(f"Removed: {job}")
            job.delete()
            return

        job.delta_synchronization = options['delta']
        if options['priority']:
            job.priority = options['priority']
        job.save()
        job.refresh_from_db()

        self.logger.info(f"New: {job}")

    def list_jobs(self):
        for job in list(SynchronizationJob.objects.all()):
            print(job)

    def set_defaults(self):
        for model, delta, priority in self.default_jobs:
            if not SynchronizationJob.objects.filter(talentmap_model=model):
                self.logger.info(f'Creating default synchronization job {model} ∆{delta} P{priority}')
                SynchronizationJob.objects.create(talentmap_model=model, delta_synchronization=delta, priority=priority)
