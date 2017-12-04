from django.core.management.base import BaseCommand
from django.core.management import call_command

import logging
import datetime

from talentmap_api.bidding.models import BidCycle
from talentmap_api.position.models import Position, Assignment
from talentmap_api.organization.models import TourOfDuty
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates demo environment - seeded users, default bidcycle'
    logger = logging.getLogger('console')

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        call_command("create_seeded_users")

        # Create bidcycle with all positions
        bc = BidCycle.objects.create(active=True,
                                     name=f"Demo BidCycle {datetime.datetime.now()}",
                                     cycle_start_date="1900-01-01",
                                     cycle_deadline_date="2100-01-01",
                                     cycle_end_date="2101-01-01")

        bc.positions.add(*list(Position.objects.all()))
        self.logger.info(f"Created demo bidcycle with all positions: {bc.name}")

        # Give all positions without a current assignment an assignment from John Doe
        profile = UserProfile.objects.get(user__username="doej")
        unassigned_positions = Position.objects.filter(current_assignment__isnull=True)
        self.logger.info(f"Creating assingments for {unassigned_positions.count()} unassigned positions...")
        for position in unassigned_positions:
            tour_of_duty = position.post.tour_of_duty
            if not tour_of_duty:
                tour_of_duty = TourOfDuty.objects.get(id=1)
            Assignment.objects.create(user=profile, position=position, start_date=datetime.datetime.now().date(), tour_of_duty=tour_of_duty, status="active")
        self.logger.info("Created.")
