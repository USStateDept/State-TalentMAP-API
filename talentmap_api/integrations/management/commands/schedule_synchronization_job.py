from django.core.management.base import BaseCommand

import logging

from talentmap_api.integrations.models import SynchronizationJob


class Command(BaseCommand):
    help = 'Creates  and updates synchronization jobs'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # Jobs, as a (model, delta) keypair
        self.default_jobs = [
            ('position.Skill', SynchronizationJob.TIME_DAY),
        ]

    def add_arguments(self, parser):
        parser.add_argument('model', nargs='?', type=str, help="The model to schedule")
        parser.add_argument('delta', nargs='?', type=int, help="The delta synchronization in seconds")
        parser.add_argument('--list', dest='list', action='store_true', help='Lists all synchronization jobs')
        parser.add_argument('--remove', dest='remove', action='store_true', help='Removes the specified model')
        parser.add_argument('--reset', dest='reset', action='store_true', help='Resets the last synchronization date on the model')
        parser.add_argument('--set-defaults', dest='set-defaults', action='store_true', help='Creates any missing baseline synchronization jobs')

    def handle(self, *args, **options):
        if options['list']:
            for job in list(SynchronizationJob.objects.all()):
                print(job)
            return

        if options['set-defaults']:
            for model, delta in self.default_jobs:
                if not SynchronizationJob.objects.filter(talentmap_model=model):
                    self.logger.info(f'Creating default synchronization job {model} ∆{delta}')
                    SynchronizationJob.objects.create(talentmap_model=model, delta_synchronization=delta)
            return

        job = SynchronizationJob.objects.get(talentmap_model=options['model'])
        if job:
            if options['reset']:
                self.logger.info(f"Resetting: {job}")
                job.last_synchronization = "1975-01-01T00:00:00Z"
                job.save()
                return

            if options['remove']:
                self.logger.info(f"Removed: {job}")
                job.delete()
                return

            self.logger.info(f"Old: {job}")
            job.delta = options['delta']
            job.save()
            job.refresh_from_db()
        else:
            job = SynchronizationJob.objects.create(model=options['model'], delta=options['delta'])
        self.logger.info(f"New: {job}")
