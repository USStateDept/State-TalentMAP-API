from django.core.management.base import BaseCommand, CommandError

import logging
import re

from talentmap_api.common.xml_helpers import XMLloader
from talentmap_api.language.models import Language, Proficiency
from talentmap_api.position.models import Grade, Skill
from talentmap_api.organization.models import Organization


class Command(BaseCommand):
    help = 'Loads an XML into a supported file'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.modes = {
            'languages': mode_languages,
            'proficiencies': mode_proficiencies,
            'grades': mode_grades,
            'skills': mode_skills,
            'organizations': mode_organizations,
        }

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The XML file to load")
        parser.add_argument('type', nargs=1, type=str, choices=self.modes.keys(), help="The type of data in the XML")

    def handle(self, *args, **options):
        model, instance_tag, tag_map, post_load_function = self.modes[options['type'][0]]()

        loader = XMLloader(model, instance_tag, tag_map)
        count = loader.create_models_from_xml(options['file'][0])

        # Run the post load function, if it exists
        if callable(post_load_function):
            post_load_function()

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

    return (model, instance_tag, tag_map, None)


def mode_proficiencies():
    model = Proficiency
    instance_tag = "LANGUAGE_PROFICIENCY:LANGUAGE_PROFICIENCY"
    tag_map = {
      "LANGUAGE_PROFICIENCY:LP_CODE": "code",
      "LANGUAGE_PROFICIENCY:LP_DESC": "description"
    }

    return (model, instance_tag, tag_map, None)


def mode_grades():
    model = Grade
    instance_tag = "GRADES:GRADE"
    tag_map = {
      "GRADES:GRD_GRADE_CODE": "code"
    }

    return (model, instance_tag, tag_map, None)


def mode_skills():
    model = Skill
    instance_tag = "SKILLS:SKILL"
    tag_map = {
        "SKILLS:SKILL_CODE": "code",
        "SKILLS:SKILL_DESCRIPTION": "description"
    }

    return (model, instance_tag, tag_map, None)


def mode_organizations():
    model = Organization
    instance_tag = "ORGS:ORGANIZATION"
    tag_map = {
        "ORGS:ORG_CODE": "code",
        "ORGS:ORG_SHORT_DESC": "short_description",
        "ORGS:ORG_LONG_DESC": lambda instance, item: setattr(instance, "long_description", re.sub(' +', ' ', item.text).strip()),
        "ORGS:ORG_PARENT_ORG_CODE": "_parent_organization_code",
        "ORGS:ORG_BUREAU_ORG_CODE": "_parent_bureau_code"
    }

    # Update relationships
    def post_load_function():
        for org in Organization.objects.all():
            org.update_relationships()

    return (model, instance_tag, tag_map, post_load_function)
