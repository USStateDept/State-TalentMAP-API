import logging

from django.core.management.base import BaseCommand
from django.core.management import call_command

from talentmap_api.integrations.models import SynchronizationJob


class Command(BaseCommand):
    help = 'Synchronizes all eligible SynchronizationJobs'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('--list', dest='list', action='store_true', help='Lists all synchronization jobs')
        parser.add_argument('--test', dest='test', action='store_true', help='Run in testing mode')
        parser.add_argument('--model', nargs='?', dest="model", help='Used to specify a model to load only the specifically requested model')

    def handle(self, *args, **options):
        if options['list']:
            for job in list(SynchronizationJob.objects.all()):
                print(job)
            return

        jobs = SynchronizationJob.get_scheduled()

        if options['model']:
            jobs = jobs.filter(talentmap_model=options['model'])

        item_count = 0
        for job in list(jobs.all()):
            if options['test']:
                self.logger.info("Running in test mode")
                item_count += job.synchronize(test=True)
            else:  # pragma: no cover
                item_count += job.synchronize()

        self.logger.info(f"Updated or created {item_count} items")
        if item_count != 0:
            self.logger.info("Now updating relationships...")
            call_command('update_relationships')
            self.logger.info("Updating string representations...")
            call_command("update_string_representations")
            self.logger.info("Clearing cache...")
            call_command('clear_cache')
