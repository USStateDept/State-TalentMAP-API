from django.core.management.base import BaseCommand

import logging
import os
import zeep

import defusedxml.lxml as ET


class Command(BaseCommand):
    help = 'Tests the connection to the SOAP webservices'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('command', nargs='?', type=str, help="The command to run")
        parser.add_argument('arguments', nargs='*', type=str, help="The arguments for the command")

    def handle(self, *args, **options):
        # Get the WSDL location
        wsdl_location = os.environ.get('WSDL_LOCATION')
        self.logger.info(f'Initializing client with WSDL: {wsdl_location}')

        client = zeep.Client(wsdl=wsdl_location)

        if not options['command']:
            self.logger.info('No command specified, dumping wsdl information')
            client.wsdl.dump()
            return

        self.logger.info(f'Calling command {options["command"]} with parameters {options["arguments"]}')
        response = getattr(client.service, options['command'])(*options['arguments'])
        self.logger.info(type(response))
        if not isinstance(response, str):
            response = ET.tostring(response, pretty_print=True)

        self.logger.info(f'SOAP call response:')
        self.logger.info(response.decode('unicode_escape'))
