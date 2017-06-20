from django.core.management.base import BaseCommand, CommandError

import logging

from talentmap_api.common.xml_helpers import XMLloader
from talentmap_api.language.models import Language, Proficiency
from talentmap_api.position.models import Grade


class Command(BaseCommand):
    help = 'Loads an XML into a supported file'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.modes = {
            'languages': mode_languages,
            'proficiencies': mode_proficiencies,
            'grades': mode_grades
        }

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The XML file to load")
        parser.add_argument('type', nargs=1, type=str, choices=self.modes.keys(), help="The type of data in the XML")

    def handle(self, *args, **options):
        model, instance_tag, tag_map = self.modes[options['type'][0]]()

        loader = XMLloader(model, instance_tag, tag_map)
        count = loader.create_models_from_xml(options['file'][0])

        self.logger.info("Loaded {} entities from {}".format(count, options['file'][0]))


def mode_languages():
    model = Language
    instance_tag = "LANGUAGES:LANGUAGE"
    tag_map = {
        "LANGUAGES:LANG_CODE": "code",
        "LANGUAGES:LANG_LONG_DESC": "long_description",
        "LANGUAGES:LANG_SHORT_DESC": "short_description",
        "LANGUAGES:LANG_EFFECTIVE_DATE": "effective_date"
    }

    return (model, instance_tag, tag_map)


def mode_proficiencies():
    model = Proficiency
    instance_tag = "LANGUAGE_PROFICIENCY:LANGUAGE_PROFICIENCY"
    tag_map = {
      "LANGUAGE_PROFICIENCY:LP_CODE": "code",
      "LANGUAGE_PROFICIENCY:LP_DESC": "description"
    }

    return (model, instance_tag, tag_map)


def mode_grades():
    model = Grade
    instance_tag = "GRADES:GRADE"
    tag_map = {
      "GRADES:GRD_GRADE_CODE": "code"
    }

    return (model, instance_tag, tag_map)
