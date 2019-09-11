'''
This file contains a variety of helper functions for data synchronization
'''

from requests import Session

import logging
import os
import re

import zeep
from zeep.transports import Transport

from dateutil.relativedelta import relativedelta

import defusedxml.lxml as ET

from django.conf import settings

from talentmap_api.common.common_helpers import ensure_date, safe_navigation
from talentmap_api.common.xml_helpers import parse_boolean, parse_date, get_nested_tag, xml_etree_to_dict, set_foreign_key_by_filters

from talentmap_api.settings import get_delineated_environment_variable

from talentmap_api.bidding.models import CyclePosition
from talentmap_api.position.models import Assignment
from talentmap_api.language.models import Proficiency
from talentmap_api.user_profile.models import SavedSearch

logger = logging.getLogger(__name__)


def get_soap_client(cert=None, soap_function="", test=False):
    '''
    Creates a properly initialized SOAP client, with unit testing support

    Args:
        - cert (str) - The location of the certificate to verify self-signed certificates (optional)
        - soap_function (str) - The name of the function that the loader will look for (optional unless testing)
        - test (bool) - Whether this is a testing SOAP client

    Returns:
        - client (Object) - The SOAP client
    '''

    client = None

    if test:
        logger.info("Creating mock SOAP client for testing")

        # Create an anonymous object
        client = type('soapclient', (object,), {})
        client.service = type('soapclientserivce', (object,), {})

        # Add the test function
        def unit_test_function(self, **kwargs):
            # Get the value from kwargs for the RequestName
            requestname = kwargs.get("RequestName")
            paginationstartkey = kwargs.get("PaginationStartKey", "")

            parser = ET._etree.XMLParser(recover=True)

            # Load the soap integration test data for that request name
            xml = os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'soap_integration', f'empty.xml')
            if paginationstartkey == "":
                xml = os.path.join(settings.BASE_DIR, 'talentmap_api', 'data', 'test_data', 'soap_integration', f'{requestname}.xml')

            xml_tree = ET.parse(xml, parser)

            return xml_tree

        # Bind the unit test function; Ash nazg thrakatulûk agh burzum-ishi krimpatul
        setattr(client.service, soap_function, unit_test_function.__get__(client.service, client.service.__class__))
    else:  # pragma: no cover
        # Initialize transport layer
        session = Session()

        # Get our Synchronization headers
        # This will search for any environment variables called DJANGO_SYNCHRONIZATION_HEADER_xxxx, and parse it as a Header/Value pair
        headers = {}
        env_sync_headers = [os.environ[key] for key in os.environ.keys() if key[:29] == "DJANGO_SYNCHRONIZATION_HEADER"]
        for header in env_sync_headers:  # pragma: no cover
            split = header.split("=")
            headers[split[0]] = split[1]
            logger.info(f"Setting Synchronization header\t\t{split[0]}: {split[1]}")

        session.headers.update(headers)

        # Attempt to get the cert location
        cert = get_delineated_environment_variable('WSDL_SSL_CERT', None)

        if cert:
            logger.info(f'Setting SSL verification cert to {cert}')
            session.verify = cert
        else:
            logger.info(f'Ignoring self-signed certification errors.')
            session.verify = False
        transport = Transport(session=session)

        # Get the WSDL location
        wsdl_location = get_delineated_environment_variable('WSDL_LOCATION')
        logger.info(f'Initializing client with WSDL: {wsdl_location}')

        client = zeep.Client(wsdl=wsdl_location, transport=transport)

        # Get our Synchronization namespace overrides
        # This will search for any environment variables called DJANGO_SOAP_NS_OVERRIDE_xxxx, and parse it as a Header/Value pair
        soap_ns_overrides = [os.environ[key] for key in os.environ.keys() if key[:23] == "DJANGO_SOAP_NS_OVERRIDE"]
        logger.info(f"Current namespace mapping {client.wsdl.types.prefix_map}")
        for override in soap_ns_overrides:  # pragma: no cover
            split = override.split("=")
            logger.info(f"Setting namespace override header\t\t{split[1]} -> {split[0]}")
            client.set_ns_prefix(split[1], client.wsdl.types.prefix_map[split[0]])
        logger.info(f"New namespace mapping {client.wsdl.types.prefix_map}")

    return client


def generate_soap_header(tag):
    '''
    Generates and returns an XSD complex type representing the requested header
    '''

    return zeep.xsd.Element(
        tag,
        zeep.xsd.String()
    )


def mode_skills(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "skill",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<skills><skill></skill></skills>"
    }

    # Response parsing data
    instance_tag = "skill"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "description": "description"
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_grade(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "grade",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<grades><grade></grade></grades>"
    }

    # Response parsing data
    instance_tag = "grade"
    collision_field = "code"
    tag_map = {
        "code": "code",
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_tods(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "tods",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<tods><tod></tod></tods>"
    }

    # Response parsing data
    instance_tag = "tod"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "short_description": "short_description",
        "long_description": lambda instance, item: setattr(instance, "long_description", re.sub('&amp;', '&', item.text).strip()),
        "months": "months",
        "status": "_status",
        "is_active": parse_boolean("is_active")
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_organizations(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "organization",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<organizations><organization></organization></organizations>"
    }

    # Response parsing data
    instance_tag = "organization"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "short_description": "short_description",
        "long_description": "long_description",
        "parent_organization": "_parent_organization_code",
        "bureau_organization": "_parent_bureau_code",
        "city_code": "_location_code",
        "is_bureau": parse_boolean("is_bureau"),
        "is_regional": parse_boolean("is_regional")
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_languages(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "language",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<languages><language></language></languages>"
    }

    # Response parsing data
    instance_tag = "language"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "long_description": "long_description",
        "short_description": "short_description",
    }

    def post_load_function(model, new_ids, updated_ids):
        # We need to ensure all appropriate proficiencies are existant
        # as there is no current SOAP synchronization endpoint for these
        Proficiency.create_defaults()

    return (soap_arguments, instance_tag, tag_map, collision_field, post_load_function, None)


def mode_countries(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "country",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<countries><country></country></countries>"
    }

    # Response parsing data
    instance_tag = "country"
    collision_field = "code"
    tag_map = tag_map = {
        "code": "code",
        "name": "name",
        "short_name": "short_name",
        "short_code": "short_code",
        "location_prefix": "location_prefix"
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_locations(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "location",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<locations><location></location></locations>"
    }

    # Response parsing data
    instance_tag = "location"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "city": "city",
        "state": "state",
        "country": "_country"
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_posts(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "orgpost",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<orgposts><orgpost></orgpost></orgposts>"
    }

    # Response parsing data
    instance_tag = "orgpost"
    collision_field = "_location_code"
    tag_map = {
        "location_code": "_location_code",
        "tod_code": set_foreign_key_by_filters("tour_of_duty", "code", "__icontains"),
        "cost_of_living_adjustment": "cost_of_living_adjustment",
        "differential_rate": "differential_rate",
        "rest_relaxation_point": "rest_relaxation_point",
        "danger_pay": "danger_pay",
        "has_consumable_allowance": parse_boolean("has_consumable_allowance"),
        "has_service_needs_differential": parse_boolean("has_service_needs_differential"),
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_capsule_descriptions(last_updated_date=None):
    # Set the appropriate use_last_updated string
    use_last_updated_string = ""
    if last_updated_date is not None:
        use_last_updated_string = f"<LAST_DATE_UPDATED>{last_updated_date}</LAST_DATE_UPDATED>"

    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "positioncapsule",
        "MaximumOutputRows": 100,
        "Version": "0.02",
        "DataFormat": "XML",
        "InputParameters": f"<positionCapsules><positionCapsule>{use_last_updated_string}</positionCapsule></positionCapsules>"
    }

    # Response parsing data
    instance_tag = "positionCapsule"
    collision_field = "_pos_seq_num"
    tag_map = {
        "POSITION_ID": "_pos_seq_num",
        "CONTENT": "content",
        "DATE_CREATED": parse_date("date_created"),
        "DATE_UPDATED": parse_date("date_updated"),
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_positions(last_updated_date=None):
    # Set the appropriate use_last_updated string
    use_last_updated_string = ""
    if last_updated_date is not None:
        use_last_updated_string = f"<LAST_DATE_UPDATED>{last_updated_date}</LAST_DATE_UPDATED>"

    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "position",
        "MaximumOutputRows": 1000,
        "Version": "0.02",
        "DataFormat": "XML",
        "InputParameters": f"<positions><position>{use_last_updated_string}</position></positions>"
    }

    # Response parsing data
    instance_tag = "position"
    collision_field = "_seq_num"
    tag_map = {
        "pos_id": "_seq_num",
        "position_number": "position_number",
        "title": "title",
        "org_code": "_org_code",
        "bureau_code": "_bureau_code",
        "skill_code": "_skill_code",
        "is_overseas": parse_boolean("is_overseas"),
        "grade": "_grade_code",
        "tod_code": set_foreign_key_by_filters("tour_of_duty", "code", "__icontains"),
        "language_code_1": "_language_1_code",
        "language_code_2": "_language_2_code",
        "location_code": "_location_code",
        "spoken_proficiency_1": "_language_1_spoken_proficiency_code",
        "reading_proficiency_1": "_language_1_reading_proficiency_code",
        "spoken_proficiency_2": "_language_2_spoken_proficiency_code",
        "reading_proficiency_2": "_language_2_reading_proficiency_code",
        "create_date": parse_date("create_date"),
        "update_date": parse_date("update_date"),
        "effective_date": parse_date("effective_date"),
    }

    def post_load_function(model, new_ids, updated_ids):
        # If we have any new or updated positions, update saved search counts
        if len(new_ids) + len(updated_ids) > 0:
            SavedSearch.update_counts_for_endpoint(endpoint='position', contains=True)

    return (soap_arguments, instance_tag, tag_map, collision_field, post_load_function, None)


def mode_skill_cones(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "jobcategoryskill",
        "MaximumOutputRows": 1000,
        "Version": "0.02",
        "DataFormat": "XML",
        "InputParameters": "<jobCategories><jobCategory></jobCategory></jobCategories>"
    }

    # Response parsing data
    instance_tag = "jobCategory"
    collision_field = "_id"
    tag_map = {
        "JC_ID": "_id",
        "JC_NM_TXT": "name",
        "skills": get_nested_tag("_skill_codes", "code", many=True)
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_cycles(last_updated_date=None):
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "cycle",
        "MaximumOutputRows": 1000,
        "Version": "0.03",
        "DataFormat": "XML",
        "InputParameters": "<cycles><cycle></cycle></cycles>"
    }

    # Response parsing data
    instance_tag = "cycle"
    collision_field = "_id"
    tag_map = {
        "id": "_id",
        "name": "name",
        "category_code": "_category_code",
        "status": "_cycle_status"
    }

    def override_loading_method(loader, tag, new_instances, updated_instances):
        # If our cycle exists, clear its position numbers
        xml_dict = xml_etree_to_dict(tag)
        extant_cycle = loader.model.objects.filter(_id=xml_dict['id']).first()
        new_status = xml_dict['status']
        if extant_cycle:
            extant_cycle._positions_seq_nums.clear()

            if extant_cycle._cycle_status != new_status:
                cycle_position = CyclePosition.objects.filter(bidcycle=extant_cycle)
                if cycle_position:
                    if new_status == 'A':
                        cycle_position.update(status_code='OP', status='OP')
                    elif new_status == 'C':
                        cycle_position.update(status_code='MC', status='MC')

        instance, updated = loader.default_xml_action(tag, new_instances, updated_instances)

        # Set active state based on cycle_status
        instance.active = instance._cycle_status == 'A'

        # Find the dates for this cycle
        for date in xml_dict["children"]:
            if date["DATA_TYPE"] == "CYCLE":
                instance.cycle_start_date = ensure_date(date["BEGIN_DATE"], utc_offset=-5)
                instance.cycle_end_date = ensure_date(date["END_DATE"], utc_offset=-5)
            elif date["DATA_TYPE"] == "BIDDUE":
                instance.cycle_deadline_date = ensure_date(date["BEGIN_DATE"], utc_offset=-5)
        if updated:
            instance.save()

    return (soap_arguments, instance_tag, tag_map, collision_field, None, override_loading_method)


def mode_cycle_positions(last_updated_date=None):
    # Set the appropriate use_last_updated string
    use_last_updated_string = ""
    if last_updated_date is not None:
        use_last_updated_string = f"<LAST_DATE_UPDATED>{last_updated_date}</LAST_DATE_UPDATED>"

    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "availableposition",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": f"<availablePositions><availablePosition>{use_last_updated_string}</availablePosition></availablePositions>"
    }

    # Response parsing data
    instance_tag = "availablePosition"
    collision_field = "_cp_id"
    tag_map = {

    }

    def post_load_function(model, new_ids, updated_ids):
        # If we have any new or updated positions, update saved search counts
        if len(new_ids) + len(updated_ids) > 0:
            SavedSearch.update_counts_for_endpoint(endpoint='cycleposition', contains=True)

    def override_loading_method(loader, tag, new_instances, updated_instances):
        data = xml_etree_to_dict(tag)
        # Find our matching bidcycle
        bc = loader.model.bidcycle.field.related_model.objects.filter(_id=data["CYCLE_ID"]).first()
        if bc:
            updated_instances.append(bc)
            bc._positions_seq_nums.append(data["POSITION_ID"])
            bc.save()

        position = loader.model.position.field.related_model.objects.filter(_seq_num=data["POSITION_ID"]).first()

        if position:
            updated_instances.append(position)
            cycle_position, _ = CyclePosition.objects.get_or_create(_cp_id=data["CP_ID"], defaults={
                'position': position,
                'bidcycle': bc,
                'status_code': data["STATUS_CODE"],
                'status': data["STATUS"],
                'created': ensure_date(data["DATE_CREATED"], utc_offset=-5),
                'updated': ensure_date(data["DATE_UPDATED"], utc_offset=-5),
                'posted_date': ensure_date(data["CP_POST_DT"], utc_offset=-5)
            })
            # if the CP was found, update it
            if _ is False:
                cycle_position.position = position
                cycle_position.bidcycle = bc
                cycle_position.status_code = data["STATUS_CODE"]
                cycle_position.status = data["STATUS"]
                cycle_position.created = ensure_date(data["DATE_CREATED"], utc_offset=-5)
                cycle_position.updated = ensure_date(data["DATE_UPDATED"], utc_offset=-5)
                cycle_position.posted_date = ensure_date(data["CP_POST_DT"], utc_offset=-5)
            position.effective_date = ensure_date(data["DATE_UPDATED"], utc_offset=-5)
            position.posted_date = ensure_date(data["CP_POST_DT"], utc_offset=-5)
            position.save()
            if "TED" in data.keys():
                ted = ensure_date(data["TED"], utc_offset=-5)
                tod = position.tour_of_duty
                if not tod:
                    tod = safe_navigation(position, "post.tour_of_duty")
                if ted and tod and tod.months:
                    cycle_position.ted = ted
                    start_date = ted - relativedelta(months=tod.months)
                    if not position.current_assignment:
                        Assignment.objects.create(position=position, start_date=start_date, tour_of_duty=tod, status="active")
                    else:
                        position.current_assignment.start_date = start_date
                        position.current_assignment.tour_of_duty = tod
                        position.current_assignment.save()
                elif ted:
                    cycle_position.ted = ted
                    logger.warning(f"Attepting to set position {position} TED to {data['TED']} but no position or post TOD is available - start date will not be set")
                    if not position.current_assignment:
                        Assignment.objects.create(position=position, estimated_end_date=ted, status="active")
                    else:
                        position.current_assignment.estimated_end_date = ted
                        position.current_assignment.state_date = None
                        position.current_assignment.tour_of_duty = None
                        position.current_assignment.save()
                else:
                    logger.warning(f"Attempting to set position {position} TED, but TED is {ted}")
            cycle_position.save()
    return (soap_arguments, instance_tag, tag_map, collision_field, post_load_function, override_loading_method)


# Model helper maps and return functions
MODEL_HELPER_MAP = {
    "position.Skill": [mode_skills],
    "position.SkillCone": [mode_skill_cones],
    "position.Grade": [mode_grade],
    "position.CapsuleDescription": [mode_capsule_descriptions],
    "organization.TourOfDuty": [mode_tods],
    "organization.Organization": [mode_organizations],
    "organization.Country": [mode_countries],
    "organization.Location": [mode_locations],
    "organization.Post": [mode_posts],
    "language.Language": [mode_languages],
    "position.Position": [mode_positions],
    "bidding.BidCycle": [mode_cycles],
    "bidding.CyclePosition": [mode_cycle_positions],
}


def get_synchronization_information(model):
    return iter(MODEL_HELPER_MAP[model])
