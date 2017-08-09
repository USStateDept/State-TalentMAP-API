from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

import logging


class Command(BaseCommand):
    help = 'Creates a user'
    logger = logging.getLogger('console')

    def add_arguments(self, parser):
        parser.add_argument('username', nargs=1, type=str, help="The username for the user")
        parser.add_argument('email', nargs=1, type=str, help="The email for the user")
        parser.add_argument('password', nargs=1, type=str, help="The desired password for the user")
        parser.add_argument('first_name', nargs=1, type=str, help="The first name for the user")
        parser.add_argument('last_name', nargs=1, type=str, help="The last name for the user")
        parser.add_argument('--settoken', dest='set_token', help='Set a specific auth token for this user')

    def handle(self, *args, **options):
        if User.objects.filter(email=options['email'][0]).count() == 0:
            user = User.objects.create_user(options['username'][0], options['email'][0], options['password'][0])
            user.first_name = options['first_name'][0]
            user.last_name = options['last_name'][0]
            user.save()
            self.logger.info(f"Successfully created {options['first_name'][0]} {options['first_name'][0]}, {options['username'][0]} ({options['email'][0]})")
            if options['set_token']:
                token = Token.objects.create(user=user, key=options['set_token'])
                self.logger.info(f"Set user's authentication token with key {token.key}")
        else:
            self.logger.info(f"User with email {options['email'][0]} already exists")
