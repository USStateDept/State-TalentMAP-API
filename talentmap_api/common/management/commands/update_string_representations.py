from django.core.management.base import BaseCommand
from django.apps import apps

import logging

from talentmap_api.common.models import StaticRepresentationModel


class Command(BaseCommand):
    help = 'Updates all models static string representations if supported'
    logger = logging.getLogger('console')

    def handle(self, *args, **options):
        models = [x for x in apps.get_models() if issubclass(x, StaticRepresentationModel)]
        for model in models:
            self.logger.info(f"Updating string representations for model: {model}")
            for instance in list(model.objects.all()):
                instance.save()

        self.logger.info("Updated string representations")
