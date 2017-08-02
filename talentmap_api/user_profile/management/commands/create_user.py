from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

import logging


class Command(BaseCommand):
    help = 'Creates a user'
    logger = logging.getLogger('console')

    def add_arguments(self, parser):
        parser.add_argument('username', nargs=1, type=str, help="The username for the user")
        parser.add_argument('email', nargs=1, type=str, help="The email for the user")
        parser.add_argument('password', nargs=1, type=str, help="The desired password for the user")

    def handle(self, *args, **options):
        if User.objects.filter(email=options['email'][0]).count() == 0:
            User.objects.create_user(options['username'][0], options['email'][0], options['password'][0])
            self.logger.info(f"Successfully created {options['username'][0]} ({options['email'][0]})")
        else:
            self.logger.info(f"User with email {options['email'][0]} already exists")
