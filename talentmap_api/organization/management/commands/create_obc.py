from django.core.management.base import BaseCommand

import logging

from talentmap_api.organization.models import Obc


class Command(BaseCommand):
    help = 'Creates OBC entries'
    logger = logging.getLogger(__name__)

    # username, email, password, firstname, lastname, is_ao, is_cdo, extra_permission_groups
    LOCATIONS = [
        ("010000101", "1"),
        ("MX1150000", "2"),
        ("040530019", "3"),
        ("MX5300000", "4"),
        ("NI0140000", "5"),
        ("NO6000000", "6"),
        ("OD0010000", "7"),
        ("PM8050000", "8"),
        ("SN1000000", "9"),
        ("TZ2000000", "10"),
        ("ZI8000000", "11"),
    ]

    def handle(self, *args, **options):
        for data in self.LOCATIONS:
            try:
                try:
                    obc = Obc.objects.get(code=data[0])
                except Obc.DoesNotExist:
                    obc = Obc.objects.create(code=data[0], obc_id=data[1])
                obc.obc_id = data[1]
                obc.save()
                self.logger.info(f"Successfully created obc with code {data[0]}, obc_id {data[1]}")
            except Exception as e:
                self.logger.info(f"Could not create {data}, {e}")

