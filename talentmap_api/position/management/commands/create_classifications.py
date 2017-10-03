from django.core.management.base import BaseCommand

import logging

from talentmap_api.position.models import Classification


class Command(BaseCommand):
    help = 'Create all position classifications'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        # A list of classifications to create
        self.classifications = [
            ("CN", "Critical Need"),
            ("DCM", "Deputy Chief of Mission"),
            ("FICA", "First In-Cone Assignment"),
            ("HDS", "Historically Difficult to Staff")
        ]

    def handle(self, *args, **options):
        for data in self.classifications:
            try:
                classification = Classification.objects.create(code=data[0], description=data[1])
                self.logger.info(f"Created classification {classification}")
            except Exception as e:
                self.logger.info(f"Error creating {data}, {e}")
