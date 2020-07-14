from django.core.management.base import BaseCommand

import logging

from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Creates application-wide permissions and groups'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.groups = [
            "bidder",
            "bureau_ao",
            "glossary_editors",
            "feedback_editors",
            "bidcycle_admin",
            "superuser",
            "bureau_user",
        ]

    def handle(self, *args, **options):
        for group_name in self.groups:
            group = Group.objects.get_or_create(name=group_name)
            if group[1]:
                self.logger.info(f"Created group {group_name}")
