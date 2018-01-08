from django.core.management.base import BaseCommand

import logging
import re

from talentmap_api.common.xml_helpers import XMLloader, strip_extra_spaces, parse_boolean, parse_date
from talentmap_api.language.models import Language, Proficiency
from talentmap_api.position.models import Grade, Skill, Position, CapsuleDescription
from talentmap_api.organization.models import Organization, Post, TourOfDuty, Location, Country


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
            'positions': mode_positions,
            'tours_of_duty': mode_tour_of_duty,
            'posts': mode_post,
            'countries': mode_country,
            'locations': mode_location,
            'capsule_descriptions': mode_capsule_description,
        }

    def add_arguments(self, parser):
        parser.add_argument('file', nargs=1, type=str, help="The XML file to load")
        parser.add_argument('type', nargs=1, type=str, choices=self.modes.keys(), help="The type of data in the XML")
        parser.add_argument('--delete', dest='delete', action='store_true', help='Delete collisions')
        parser.add_argument('--update', dest='update', action='store_true', help='Update collisions')
        parser.add_argument('--skippost', dest='skip_post', action='store_true', help='Skip post load functions')

    def handle(self, *args, **options):
        model, instance_tag, tag_map, collision_field, post_load_function = self.modes[options['type'][0]]()

        # Set / update the collision behavior
        collision_behavior = None
        if options['delete']:
            collision_behavior = "delete"
        elif options['update']:
            collision_behavior = "update"
        else:
            collision_behavior = "skip"

        loader = XMLloader(model, instance_tag, tag_map, collision_behavior, collision_field)
        new_ids, updated_ids = loader.create_models_from_xml(options['file'][0])

        # Run the post load function, if it exists
        if callable(post_load_function) and not options['skip_post']:
            post_load_function(new_ids, updated_ids)

        self.logger.info(f"XML Load Report\n\tNew: {len(new_ids)}\n\tUpdated: {len(updated_ids)}\t\t")


def mode_languages():
    model = Language
    instance_tag = "LANGUAGES:LANGUAGE"
    collision_field = "code"
    tag_map = {
        "LANGUAGES:LANG_CODE": "code",
        "LANGUAGES:LANG_LONG_DESC": "long_description",
        "LANGUAGES:LANG_SHORT_DESC": "short_description",
        "LANGUAGES:LANG_EFFECTIVE_DATE": parse_date("effective_date")
    }

    return (model, instance_tag, tag_map, collision_field, None)


def mode_proficiencies():
    model = Proficiency
    instance_tag = "LANGUAGE_PROFICIENCY:LANGUAGE_PROFICIENCY"
    collision_field = "code"
    tag_map = {
        "LANGUAGE_PROFICIENCY:LP_CODE": "code",
        "LANGUAGE_PROFICIENCY:LP_DESC": "description"
    }

    return (model, instance_tag, tag_map, collision_field, None)


def mode_grades():
    model = Grade
    instance_tag = "GRADES:GRADE"
    collision_field = "code"
    tag_map = {
        "GRADES:GRD_GRADE_CODE": "code"
    }

    def post_load_function(new_ids, updated_ids):
        for pos in Grade.objects.filter(id__in=new_ids + updated_ids):
            pos.update_relationships()

    return (model, instance_tag, tag_map, collision_field, post_load_function)


def mode_skills():
    model = Skill
    instance_tag = "SKILLS:SKILL"
    collision_field = "code"
    tag_map = {
        "SKILLS:SKILL_CODE": "code",
        "SKILLS:SKILL_DESCRIPTION": "description"
    }

    return (model, instance_tag, tag_map, collision_field, None)


def mode_organizations():
    model = Organization
    instance_tag = "DATA_RECORD"
    collision_field = "code"
    tag_map = {
        "ORG_CODE": "code",
        "ORG_SHORT_DESC": "short_description",
        "ORG_LONG_DESC": strip_extra_spaces("long_description"),
        "ORG_PARENT_ORG_CODE": "_parent_organization_code",
        "ORG_BUREAU_ORG_CODE": "_parent_bureau_code",
        "ORG_LOCATION_CODE": "_location_code"
    }

    # Update relationships
    def post_load_function(new_ids, updated_ids):
        for org in Organization.objects.filter(id__in=new_ids + updated_ids):
            org.update_relationships()

    return (model, instance_tag, tag_map, collision_field, post_load_function)


def mode_positions():
    model = Position
    instance_tag = "POSITIONS:POSITION"
    collision_field = "_seq_num"
    tag_map = {
        "POSITIONS:POS_SEQ_NUM": "_seq_num",
        "POSITIONS:POS_NUM_TEXT": "position_number",
        "POSITIONS:POS_TITLE_CODE": "_title_code",
        "POSITIONS:POS_TITLE_DESC": "title",
        "POSITIONS:POS_ORG_CODE": "_org_code",
        "POSITIONS:POS_BUREAU_CODE": "_bureau_code",
        "POSITIONS:POS_SKILL_CODE": "_skill_code",
        "POSITIONS:POS_STAFF_PTRN_SKILL_CODE": "_staff_ptrn_skill_code",
        "POSITIONS:POS_OVERSEAS_IND": parse_boolean("is_overseas", ['O']),
        "POSITIONS:POS_PAY_PLAN_CODE": "_pay_plan_code",
        "POSITIONS:POS_STATUS_CODE": "_status_code",
        "POSITIONS:POS_SERVICE_TYPE_CODE": "_service_type_code",
        "POSITIONS:POS_GRADE_CODE": "_grade_code",
        "POSITIONS:POS_POST_CODE": "_post_code",
        "POSITIONS:POS_LANGUAGE_1_CODE": "_language_1_code",
        "POSITIONS:POS_LANGUAGE_2_CODE": "_language_2_code",
        "POSITIONS:POS_LOCATION_CODE": "_location_code",
        "POSITIONS:POS_LANG_REQ_1_CODE": "_language_req_1_code",
        "POSITIONS:POS_LANG_REQ_2_CODE": "_language_req_2_code",
        "POSITIONS:POS_SPEAK_PROFICIENCY_1_CODE": "_language_1_spoken_proficiency_code",
        "POSITIONS:POS_READ_PROFICIENCY_1_CODE": "_language_1_reading_proficiency_code",
        "POSITIONS:POS_SPEAK_PROFICIENCY_2_CODE": "_language_2_spoken_proficiency_code",
        "POSITIONS:POS_READ_PROFICIENCY_2_CODE": "_language_2_reading_proficiency_code",
        "POSITIONS:POS_CREATE_ID": "_create_id",
        "POSITIONS:POS_CREATE_DATE": parse_date("create_date"),
        "POSITIONS:POS_UPDATE_ID": "_update_id",
        "POSITIONS:POS_UPDATE_DATE": parse_date("update_date"),
        "POSITIONS:POS_EFFECTIVE_DATE": parse_date("effective_date"),
        "POSITIONS:POS_JOBCODE_CODE": "_jobcode_code",
        "POSITIONS:POS_OCC_SERIES_CODE": "_occ_series_code",
    }

    def post_load_function(new_ids, updated_ids):
        for pos in Position.objects.filter(id__in=new_ids + updated_ids):
            pos.update_relationships()

    return (model, instance_tag, tag_map, collision_field, post_load_function)


def mode_tour_of_duty():
    model = TourOfDuty
    instance_tag = "TOUR_OF_DUTIES:TOUR_OF_DUTY"
    collision_field = "code"
    tag_map = {
        "TOUR_OF_DUTIES:TOD_CODE": "code",
        "TOUR_OF_DUTIES:TOD_SHORT_DESC": "short_description",
        "TOUR_OF_DUTIES:TOD_DESC_TEXT": lambda instance, item: setattr(instance, "long_description", re.sub('&amp;', '&', item.text).strip()),
        "TOUR_OF_DUTIES:TOD_MONTHS_NUM": "months"
    }

    return (model, instance_tag, tag_map, collision_field, None)


def mode_post():
    model = Post
    instance_tag = "BIDPOSTS:BIDDING_TOOL"
    collision_field = "_location_code"
    tag_map = {
        "BIDPOSTS:DSC_CD": "_location_code",
        "BIDPOSTS:TOD_CODE": "_tod_code",
        "BIDPOSTS:BT_COST_OF_LIVING_ADJUST_NUM": "cost_of_living_adjustment",
        "BIDPOSTS:BT_DIFFERENTIAL_RATE_NUM": "differential_rate",
        "BIDPOSTS:BT_REST_RELAXATION_POINT_TEXT": strip_extra_spaces("rest_relaxation_point"),
        "BIDPOSTS:BT_DANGER_PAY_NUM": "danger_pay",
        "BIDPOSTS:BT_CONSUMABLE_ALLOWANCE_FLG": parse_boolean("has_consumable_allowance"),
        "BIDPOSTS:BT_SERVICE_NEEDS_DIFF_FLG": parse_boolean("has_service_needs_differential"),
    }

    def post_load_function(new_ids, updated_ids):
        for loc in Post.objects.filter(id__in=new_ids + updated_ids):
            loc.update_relationships()

    return (model, instance_tag, tag_map, collision_field, post_load_function)


def mode_country():
    model = Country
    instance_tag = "DATA_RECORD"
    collision_field = "code"
    tag_map = {
        "COUNTRY_CODE": "code",
        "FULL_NAME": "name",
        "SHORT_NAME": "short_name",
        "COUNTRY_CODE_2": "short_code",
        "LOCATION_PREFIX": "location_prefix"
    }

    return (model, instance_tag, tag_map, collision_field, None)


def mode_location():
    model = Location
    instance_tag = "location"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "city": strip_extra_spaces("city"),
        "state": strip_extra_spaces("state"),
        "country": "_country"
    }

    def post_load_function(new_ids, updated_ids):
        # Connect new locations to applicable posts
        for loc in Location.objects.filter(id__in=new_ids + updated_ids):
            Post.objects.filter(_location_code=loc.code).update(location=loc)

    return (model, instance_tag, tag_map, collision_field, post_load_function)


def mode_capsule_description():
    model = CapsuleDescription
    instance_tag = "position"
    collision_field = "_pos_seq_num"
    tag_map = {
        "POS_SEQ_NUM": "_pos_seq_num",
        "capsuleDescription": "content",
    }

    return (model, instance_tag, tag_map, collision_field, None)
