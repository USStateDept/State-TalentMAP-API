from django.core.management.base import BaseCommand

import logging
import csv

from talentmap_api.common.xml_helpers import CSVloader
from talentmap_api.organization.models import Post, Country


class Command(BaseCommand):
    help = 'Loads a CSV into a supported model'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.modes = {
            'post': Post,
            'country': Country,
        }

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The CSV file to load")
        parser.add_argument('type', nargs=1, type=str, choices=self.modes.keys(), help="The type of data in the CSV")

    def handle(self, *args, **options):
        # Parse the CSV
        with open(options['file'][0], 'r') as csv_file:
            model = self.modes[options['type'][0]]
            count = 0
            for line in csv.DictReader(csv_file):
                search_terms = (line["description"] + line["aux"]).split(" ")
                instance = model.objects.filter(_string_representation__search=line["description"])
                if instance.count() != 1:
                    instance = model.objects.all()
                    for term in search_terms:
                        instance = instance.filter(_string_representation__icontains=term)
                        if instance.count() == 1:
                            break
                if instance.count() == 0:
                    self.logger.info(f"Could not find {model} for {line['description']}")
                elif instance.count() > 1:
                    self.logger.info(f"Found multiple matches for {line['description']}")
                    self.logger.info(instance)
                else:
                    instance = instance.first()
                    instance.obc_id = line["obc_id"]
                    count = count + 1
                    instance.save()

        self.logger.info(f"CSV Load Report\n\tLoaded: {count}\t\t")
