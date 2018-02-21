from django.core.management.base import BaseCommand

import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Creates application-wide superuser role'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('email', nargs=1, type=str, help="The super user's e-mail")

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="superuser")
        if created:
            self.logger.info(f"Created group superuser")

        User.objects.get(email=options['email'][0]).groups.add(group)
