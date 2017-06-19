from django.core.management.base import BaseCommand, CommandError

import logging

from talentmap_api.common.xml_helpers import XMLloader
from talentmap_api.language.models import Language, Proficiency


class Command(BaseCommand):
    help = 'Loads a list of languages or proficiencies from an XML file into the database'
    logger = logging.getLogger('console')

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The XML file to load")
        parser.add_argument('type', nargs=1, type=str, choices=['languages', 'proficiencies'], help="The type of data in the XML")

    def handle(self, *args, **options):
        tag_map = {}
        instance_tag = ""
        model = None

        # Set the tag map according to the 'type' selected
        if options['type'][0] == 'languages':
            model = Language
            instance_tag = "LANGUAGES:LANGUAGE"
            tag_map = {
                "LANGUAGES:LANG_CODE": "code",
                "LANGUAGES:LANG_LONG_DESC": "long_description",
                "LANGUAGES:LANG_SHORT_DESC": "short_description",
                "LANGUAGES:LANG_EFFECTIVE_DATE": "effective_date"
            }
        elif options['type'][0] == 'proficiencies':
            model = Proficiency
            instance_tag = "LANGUAGE_PROFICIENCY:LANGUAGE_PROFICIENCY"
            tag_map = {
              "LANGUAGE_PROFICIENCY:LP_CODE": "code",
              "LANGUAGE_PROFICIENCY:LP_DESC": "description"
            }

        loader = XMLloader(model, instance_tag, tag_map)
        count = loader.create_models_from_xml(options['file'][0])

        self.logger.info("Loaded {} entities from {}".format(count, options['file'][0]))
