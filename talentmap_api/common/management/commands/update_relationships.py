from django.core.management.base import BaseCommand

import logging

from talentmap_api.position.models import Position, Grade, SkillCone
from talentmap_api.organization.models import Organization, Post, Location


class Command(BaseCommand):
    help = 'Updates all models foreign key relationships'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # These models should have update_relationships
        self.models = [
            Organization,
            Position,
            Location,
            Post,
            Grade,
            SkillCone
        ]

    def handle(self, *args, **options):
        for model in self.models:
            self.logger.info(f"Updating model: {model.__name__}")
            for instance in model.objects.all():
                instance.update_relationships()

        self.logger.info("Updated relationships")
