from django.core.management.base import BaseCommand
from django.apps import apps

import logging

from talentmap_api.bidding.models import BidCycle
from talentmap_api.position.models import Position, Grade, SkillCone
from talentmap_api.organization.models import Organization, OrganizationGroup, Post, Location


class Command(BaseCommand):
    help = 'Updates all models foreign key relationships'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # These models should have update_relationships
        self.models = [
            Organization,
            OrganizationGroup,
            Position,
            Location,
            Post,
            Grade,
            SkillCone,
        ]
    def add_arguments(self, parser):
        parser.add_argument('--model', nargs='?', dest="model", help='Used to specify a model to process only the specifically requested model')

    def handle(self, *args, **options):
        models = self.models
        if options['model']:
            try:
                m = apps.get_model(options['model'])
            except (LookupError, ValueError):
                print(f"The model {options['model']} could not be found. Available models are:")
                for o in self.models:
                    print(f"\t{o._meta.app_label}.{o.__name__}")
                return

            if m in models:
                models = [m]
            else:
                print(f"The model {options['model']} is not in the models array and does not have an update_relationships function")
                return
        
        for model in models:
            self.logger.info(f"Updating model: {model.__name__}")
            for instance in model.objects.all():
                instance.update_relationships()

        self.logger.info("Updated relationships")
