from django.core.management.base import BaseCommand

import logging
import os
import zeep

import defusedxml.lxml as ET

from requests import Session
from zeep.transports import Transport

from talentmap_api.common.common_helpers import xml_etree_to_dict

class Command(BaseCommand):
    help = 'Tests the connection to the SOAP webservices'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('command', nargs='?', type=str, help="The command to run")
        parser.add_argument('arguments', nargs='*', type=str, help="The arguments for the command, as named pairs; i.e. USCity=Fairfax")

    def handle(self, *args, **options):
        # Initialize transport layer
        session = Session()
        # Uncomment the following line if we're verifying a self signed certificate
        # session.verify = 'path_to_self_signed.cert'
        session.verify = False
        transport = Transport(session=session)

        # Get the WSDL location
        wsdl_location = os.environ.get('WSDL_LOCATION')
        self.logger.info(f'Initializing client with WSDL: {wsdl_location}')

        client = zeep.Client(wsdl=wsdl_location, transport=transport)

        if not options['command']:
            self.logger.info('No command specified, dumping wsdl information')
            client.wsdl.dump()
            return

        arguments = {x.split('=')[0]: x.split('=')[1] for x in options["arguments"]}
        self.logger.info(f'Calling command {options["command"]} with parameters {arguments}')
        response = getattr(client.service, options['command'])(**arguments)
        dict_response = xml_etree_to_dict(response)
        self.logger.info(type(response))
        if not isinstance(response, str):
            response = ET.tostring(response, pretty_print=True)

        self.logger.info(f'SOAP call response:')
        self.logger.info(response.decode('unicode_escape'))

        self.logger.info(f'Dictionary parsed response: {dict_response}')
