from django.core.management.base import BaseCommand
from django.apps import apps

import logging

from talentmap_api.common.models import StaticRepresentationModel


class Command(BaseCommand):
    help = 'Updates all models static string representations if supported'
    logger = logging.getLogger(__name__)
    
    def add_arguments(self, parser):
        parser.add_argument('--model', nargs='?', dest="model", help='Used to specify a model to process only the specifically requested model')
    
    def handle(self, *args, **options):
        if options['model']:
            try:
                m = apps.get_model(options['model'])
            except (LookupError, ValueError):
                print(f"The model {options['model']} could not be found")
                return

            if issubclass(m, StaticRepresentationModel):
                models = [m]
            else:
                print(f"The model {options['model']} is not a subclass of StaticRepresentationModel")
                return
        else:
            models = [x for x in apps.get_models() if issubclass(x, StaticRepresentationModel)]
        for model in models:
            self.logger.info(f"Updating string representations for model: {model}")
            for instance in list(model.objects.all()):
                instance.save()

        self.logger.info("Updated string representations")
