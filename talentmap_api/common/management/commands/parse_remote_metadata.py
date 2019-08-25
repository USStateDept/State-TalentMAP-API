from django.core.management.base import BaseCommand

import logging
import re

class Command(BaseCommand):
    help = 'Parses remote metadata into a basic dictionary for mapping'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The XML file to read")

    def handle(self, *args, **options):
        search_pattern = r"<Attribute Name=\"([^\"]+)\"\sNameFormat=\"([^\"]+)\"\sFriendlyName=\"([^\"]+)\"\sxmlns=\"([^\"]+)\"/>"
        pattern = re.compile(search_pattern)

        with open(options['file'][0], 'r') as f:
            data = f.readlines()

        print(f"Read {len(data)} lines")
        for line in data:
            for match in pattern.finditer(line):
                uri = match.group(1)
                frmt = match.group(2)
                friendly = match.group(3)
                name = uri.split("/")[-1]

                print(f'"{uri}": "{name}",  # {friendly}, {frmt}')
