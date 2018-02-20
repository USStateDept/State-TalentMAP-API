from django.core.management.base import BaseCommand

import logging

from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Creates application-wide superuser role'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        group = Group.objects.get_or_create(name="superuser")
        if group[1]:
            self.logger.info(f"Created group superuser")
