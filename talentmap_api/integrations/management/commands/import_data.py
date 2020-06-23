import logging

from django.core.management.base import BaseCommand

# from talentmap_api.integrations.models import ImportModel


class Command(BaseCommand):
    help = 'Imports data for all non imported raw data'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('--list', dest='list', action='store_true', help='Lists all data sets requiring import')
        parser.add_argument('--model', nargs='?', dest="model", help='Used to specify a model to load only the specifically requested model')

    def handle(self, *args, **options):
        pass
        # if options['list']:
        #     for job in list(ImportModel.objects.all()):
        #         print(job)
        #     return

        # jobs = ImportModel.get_unimported()

        # if options['model']:
        #     jobs = jobs.filter(source_endpoint=options['model'])

        # item_count = 0
        # for job in list(jobs.all()):
        #     self.logger.info(f"Importing data for {job.source_endpoint}")
        #     items_imported = job.import_raw_data()
        #     self.logger.info(f"Imported {items_imported}")
        #     item_count += items_imported
        #     job.imported = True
        #     job.save()

        # self.logger.info(f"Updated or created {item_count} total items")
        # if item_count != 0:
        #     self.logger.info("Now updating relationships...")
        #     call_command('update_relationships')
        #     self.logger.info("Updating string representations...")
        #     call_command("update_string_representations")
        #     self.logger.info("Clearing cache...")
        #     call_command('clear_cache')
