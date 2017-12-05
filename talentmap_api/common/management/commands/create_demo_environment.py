from django.core.management.base import BaseCommand
from django.core.management import call_command

import logging
import datetime
import itertools

from talentmap_api.bidding.models import BidCycle, Bid
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

        self.logger.info(f"Seeding bids for all users...")
        # Remove any existing bids
        Bid.objects.all().delete()

        # Create 5 bids for each user
        positions = list(bc.positions.order_by('?'))
        for user in list(UserProfile.objects.all()):
            for _ in range(0, 5):
                Bid.objects.create(position=positions.pop(), bidcycle=bc, user=user)
        self.logger.info(f"Seeded bids, randomly altering statuses...")
        # Assign random bids statuses
        statuses = itertools.cycle([Bid.Status.submitted, Bid.Status.handshake_offered])
        for bid in list(Bid.objects.exclude(user__user__username__in=["admin", "doej", "guest"]).order_by('?')[:10]):
            bid.status = next(statuses)
            self.logger.info(f"Setting status: {bid}")
            bid.save()

        self.logger.info("Done initializing bids")
