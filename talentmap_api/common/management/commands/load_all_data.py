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
            'organizations': ['organization.xml', 'regional_bureaus.xml'],
            'tours_of_duty': 'tour_of_duty.xml',
            'posts': 'bidding_tool.xml',
            'positions': 'position.xml',
        }

        # File modes whose post load function should be skipped during this load
        # This is useful for those whose post-load function sets up foreign key
        # linkages, as we manually call that afterwards regardless
        self.skippost = ['organizations', 'positions', 'posts']

    def add_arguments(self, parser):
        parser.add_argument('filepath', nargs=1, type=str, help="The directory containing the XML files")
        parser.add_argument('--delete', dest='delete', action='store_true', help='Delete collisions')
        parser.add_argument('--update', dest='update', action='store_true', help='Update collisions')

    def handle(self, *args, **options):
        for mode in self.files.keys():
            filelist = self.files[mode]
            if not isinstance(filelist, list):
                filelist = [filelist]
            for fileinstance in filelist:
                self.logger.info(f"Now loading {fileinstance} ({mode})")
                try:
                    command_opts = [
                        'load_xml',
                        os.path.join(options['filepath'][0], fileinstance),
                        mode
                    ]
                    if mode in self.skippost:
                        command_opts.append('--skippost')
                    if options['update']:
                        command_opts.append('--update')
                    if options['delete']:
                        command_opts.append('--delete')
                    call_command(*command_opts)
                except Exception as e:
                    self.logger.info(f"Failed to load {fileinstance} ({mode}): {e}")
        self.logger.info("Now updating relationships...")
        call_command('update_relationships')
