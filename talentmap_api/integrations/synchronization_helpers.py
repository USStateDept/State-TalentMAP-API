'''
This file contains a variety of helper functions for data synchronization
'''

from requests import Session

import logging
import os

import zeep
from zeep.transports import Transport


def get_soap_client(cert=None):
    '''
    Creates a properly initialized SOAP client

    Args:
        - cert (str) - The location of the certificate to verify self-signed certificates (optional)

    Returns:
        - client (Object) - The SOAP client
    '''

    logger = logging.getLogger('console')

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


# Model helper maps and return functions
MODEL_HELPER_MAP = {
    "position.Skill": mode_skills
}


def get_synchronization_information(model):
    return MODEL_HELPER_MAP[model]()
