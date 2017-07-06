from django.core.management.base import BaseCommand, CommandError

import logging
import re
import os

from django.core.management import call_command


class Command(BaseCommand):
    help = 'Loads all data using the load_xml command from files stored in a given folder'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # These models should have update_relationships
        self.files = {
            'languages': 'language.xml',
            'proficiencies': 'language_proficiency.xml',
            'grades': 'grade.xml',
            'skills': 'skill.xml',
            'organizations': 'organization.xml',
            'tours_of_duty': 'tour_of_duty.xml',
            'posts': 'bidding_tool.xml',
            'positions': 'position.xml',
        }

    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs=1, type=str, help="The directory containing the XML files")

    def handle(self, *args, **options):
        for mode in self.files.keys():
            self.logger.info(f"Now loading {mode}")
            try:
                call_command('load_xml',
                             os.path.join(options['filepath'][0], self.files[mode]),
                             mode)
            except Exception as e:
                self.logger.info(f"Failed to load {mode}: {e}")
