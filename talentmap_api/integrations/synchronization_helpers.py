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

from talentmap_api.common.xml_helpers import strip_extra_spaces, parse_boolean

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
        setattr(client, soap_function, unit_test_function.__get__(client, client.__class__))
    else:  # pragma: no cover
        # Initialize transport layer
        session = Session()

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

    return client


def mode_skills():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "skill",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<skills><skill></skill></skills>]]>"
    }

    # Response parsing data
    instance_tag = "skill"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "description": "description"
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_grade():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "grade",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<grades><grade></grade></grades>]]>"
    }

    # Response parsing data
    instance_tag = "grade"
    collision_field = "code"
    tag_map = {
        "code": "code",
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_tods():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "tods",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<tods><tod></tod></tods>]]>"
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

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_organizations():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "organization",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<organizations><organization></organization></organizations>]]>"
    }

    # Response parsing data
    instance_tag = "organization"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "short_description": "short_description",
        "long_description": strip_extra_spaces("long_description"),
        "parent_organization": "_parent_organization_code",
        "bureau_organization": "_parent_bureau_code",
        "city_code": "_location_code",
        "is_bureau": parse_boolean("is_bureau"),
        "is_regional": parse_boolean("is_regional")
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_languages():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "language",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<languages><language></language></languages>]]>"
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

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_countries():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "country",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<countries><country></country></countries>]]>"
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

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_locations():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "location",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<locations><location></location></locations>]]>"
    }

    # Response parsing data
    instance_tag = "location"
    collision_field = "code"
    tag_map = {
        "code": "code",
        "city": strip_extra_spaces("city"),
        "state": strip_extra_spaces("state"),
        "country": "_country"
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


def mode_posts():
    # Request data
    soap_arguments = {
        "RequestorID": "TalentMAP",
        "Action": "GET",
        "RequestName": "orgpost",
        "Version": "0.01",
        "DataFormat": "XML",
        "InputParameters": "<![CDATA[<orgposts><orgpost></orgpost></orgposts>]]>"
    }

    # Response parsing data
    instance_tag = "orgpost"
    collision_field = "_location_code"
    tag_map = {
        "location_code": "_location_code",
        "tod_code": "_tod_code",
        "cost_of_living_adjustment": "cost_of_living_adjustment",
        "differential_rate": "differential_rate",
        "rest_relaxation_point": strip_extra_spaces("rest_relaxation_point"),
        "danger_pay": "danger_pay",
        "has_consumable_allowance": parse_boolean("has_consumable_allowance"),
        "has_service_needs_differential": parse_boolean("has_service_needs_differential"),
    }

    return (soap_arguments, instance_tag, tag_map, collision_field, None)


# Model helper maps and return functions
MODEL_HELPER_MAP = {
    "position.Skill": mode_skills,
    "position.Grade": mode_grade,
    "organization.TourOfDuty": mode_tods,
    "organization.Organization": mode_organizations,
    "organization.Country": mode_countries,
    "organization.Location": mode_locations,
    "organization.Post": mode_posts,
    "language.Language": mode_languages,
}


def get_synchronization_information(model):
    return MODEL_HELPER_MAP[model]()
