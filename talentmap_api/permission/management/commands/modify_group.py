from django.core.management.base import BaseCommand

import logging

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Add or remove a user (by email) from a group'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('mode', nargs=1, type=str, choices=['add', 'remove'], help="The mode [add/remove]")
        parser.add_argument('email', nargs=1, type=str, help="The user's e-mail")
        parser.add_argument('group', nargs=1, type=str, help="The group name")

    def handle(self, *args, **options):
        group = Group.objects.get(name=options['group'][0])
        if group:
            self.logger.info(f"Group modficiation command: {options['mode'][0]} {options['email'][0]} to {options['group'][0]}")
            if options['mode'][0] == 'add':
                User.objects.get(email=options['email'][0]).groups.add(group)
            else:
                User.objects.get(email=options['email'][0]).groups.remove(group)
