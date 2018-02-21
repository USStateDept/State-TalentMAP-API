'''
This file contains a variety of helper functions for data synchronization
'''

from requests import Session

import logging
import os
import re

import zeep
from zeep.transports import Transport

import defusedxml.lxml as ET

from django.conf import settings

from talentmap_api.common.common_helpers import ensure_date
from talentmap_api.common.xml_helpers import parse_boolean, parse_date, get_nested_tag, xml_etree_to_dict

from talentmap_api.language.models import Proficiency


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

    logger = logging.getLogger('console')

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
        cert = os.environ.get('WSDL_SSL_CERT', None)

        if cert:
            logger.info(f'Setting SSL verification cert to {cert}')
            session.verify = cert
        else:
            logger.info(f'Ignoring self-signed certification errors.')
            session.verify = False
        transport = Transport(session=session)

        # Get the WSDL location
        wsdl_location = os.environ.get('WSDL_LOCATION')
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


def mode_skills():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "skill",
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


def mode_grade():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "grade",
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


def mode_tods():
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


def mode_organizations():
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


def mode_languages():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "language",
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


def mode_countries():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "country",
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


def mode_locations():
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


def mode_posts():
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
        "tod_code": "_tod_code",
        "cost_of_living_adjustment": "cost_of_living_adjustment",
        "differential_rate": "differential_rate",
        "rest_relaxation_point": "rest_relaxation_point",
        "danger_pay": "danger_pay",
        "has_consumable_allowance": parse_boolean("has_consumable_allowance"),
        "has_service_needs_differential": parse_boolean("has_service_needs_differential"),
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_capsule_descriptions():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "positioncapsule",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<positionCapsules><positionCapsule></positionCapsule></positionCapsules>"
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


def mode_positions():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "position",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<positions><position></position></positions>"
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
        "is_overseas": parse_boolean("is_overseas", ['O']),
        "grade": "_grade_code",
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

    return (soap_arguments, instance_tag, tag_map, collision_field, None, None)


def mode_skill_cones():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "jobcategoryskill",
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


def mode_cycles():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "cycle",
        "Version": "0.02",
        "DataFormat": "XML",
        "InputParameters": "<cycles><cycle></cycle></cycles>"
    }

    # Response parsing data
    instance_tag = "cycle"
    collision_field = "_id"
    tag_map = {
        "id": "_id",
        "name": "name",
        "category_code": "_category_code"
    }

    def override_loading_method(loader, tag, new_instances, updated_instances):
        # If our cycle exists, clear it's position numbers
        xml_dict = xml_etree_to_dict(tag)
        extant_cycle = loader.model.objects.filter(_id=xml_dict['id']).first()
        if extant_cycle:
            extant_cycle._positions_seq_nums.clear()

        instance, updated = loader.default_xml_action(tag, new_instances, updated_instances)

        # Find the dates for this cycle
        for date in xml_dict["children"]:
            if date["DATA_TYPE"] == "CYCLE":
                instance.cycle_start_date = ensure_date(date["BEGIN_DATE"])
                instance.cycle_end_date = ensure_date(date["END_DATE"])
            elif date["DATA_TYPE"] == "BIDDUE":
                instance.cycle_deadline_date = ensure_date(date["BEGIN_DATE"])
        if updated:
            instance.save()

    return (soap_arguments, instance_tag, tag_map, collision_field, None, override_loading_method)


def mode_cycle_positions():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "availableposition",
        "MaximumOutputRows": 1000,
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<availablePositions><availablePosition></availablePosition></availablePositions>"
    }

    # Response parsing data
    instance_tag = "availablePosition"
    collision_field = ""
    tag_map = {

    }

    def override_loading_method(loader, tag, new_instances, updated_instances):
        data = xml_etree_to_dict(tag)
        # Find our matching bidcycle
        bc = loader.model.objects.filter(_id=data["CYCLE_ID"]).first()
        if bc:
            bc._positions_seq_nums.append(data["POSITION_ID"])
            bc.save()

    return (soap_arguments, instance_tag, tag_map, collision_field, None, override_loading_method)


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
    "bidding.BidCycle": [mode_cycles, mode_cycle_positions],
}


def get_synchronization_information(model):
    return iter(MODEL_HELPER_MAP[model])
