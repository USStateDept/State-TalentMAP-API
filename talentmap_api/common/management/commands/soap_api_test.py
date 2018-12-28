from django.core.management.base import BaseCommand

import logging
import pprint

import defusedxml.lxml as ET

from talentmap_api.common.common_helpers import xml_etree_to_dict
from talentmap_api.integrations.synchronization_helpers import get_soap_client


class Command(BaseCommand):
    help = 'Tests the connection to the SOAP webservices'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('command', nargs='?', type=str, help="The command to run")
        parser.add_argument('arguments', nargs='*', type=str, help="The arguments for the command, as named pairs; i.e. USCity=Fairfax")

    def handle(self, *args, **options):
        client = get_soap_client()
        pp = pprint.PrettyPrinter(indent=2)

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

        self.logger.info(f'Dictionary parsed response: {pp.pformat(dict_response)}')
