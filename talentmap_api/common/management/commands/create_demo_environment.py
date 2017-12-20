from django.core.management.base import BaseCommand
from django.core.management import call_command

import logging
import datetime
import itertools

from talentmap_api.bidding.models import BidCycle, Bid, Waiver
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
        BidCycle.objects.all().delete()
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
        self.logger.info(f"Creating assignments for {unassigned_positions.count()} unassigned positions...")
        for position in unassigned_positions:
            tour_of_duty = position.post.tour_of_duty
            if not tour_of_duty:
                tour_of_duty = TourOfDuty.objects.get(id=1)
            Assignment.objects.create(user=profile, position=position, start_date=datetime.datetime.now().date(), tour_of_duty=tour_of_duty, status="active")
        self.logger.info("Created.")

        self.logger.info(f"Seeding bids for all users...")
        valid_users = itertools.cycle(list(UserProfile.objects.exclude(user__username__in=["admin", "doej", "guest", "woodwardw"]).all()))

        # Remove any existing bids
        Bid.objects.all().delete()

        # Create 40 bids, with competition
        positions = list(bc.positions.filter(bureau__code="150000").order_by('?'))  # Our AO persona gets all the bids
        for _ in range(0, 20):
            position = positions.pop()
            Bid.objects.create(position=position, bidcycle=bc, user=next(valid_users))
            Bid.objects.create(position=position, bidcycle=bc, user=next(valid_users))
        self.logger.info(f"Seeded bids, randomly altering statuses...")
        # Assign random bids statuses
        statuses = itertools.cycle([Bid.Status.submitted, Bid.Status.handshake_offered])
        for bid in list(Bid.objects.all().order_by('?')[:20]):
            bid.status = next(statuses)
            setattr(bid, f"{bid.status}_date", datetime.datetime.now().date())
            self.logger.info(f"Setting bid status: {bid}")
            bid.save()

        # Move one bid through the entire process
        bid = Bid.objects.exclude(user__user__username='woodwardw').filter(status=Bid.Status.submitted).first()
        self.logger.info(f"Walking through bid process with {bid.id} {bid}")
        bid.status = Bid.Status.handshake_offered
        bid.handshake_offered_date = datetime.datetime.now().date()
        bid.save()

        bid.status = Bid.Status.handshake_accepted
        bid.handshake_accepted_date = datetime.datetime.now().date()
        bid.save()

        bid.status = Bid.Status.in_panel
        bid.in_panel_date = datetime.datetime.now().date()
        bid.scheduled_panel_date = "2017-12-25"
        bid.save()

        # Reschedule the bid
        bid.scheduled_panel_date = "2018-01-20"
        bid.save()

        bid.status = Bid.Status.approved
        bid.approved_date = datetime.datetime.now().date()
        bid.save()

        self.logger.info("Done initializing bids")

        self.logger.info("Seeding waiver requests...")
        Waiver.objects.all().delete()

        waiver_status = itertools.cycle([Waiver.Status.requested, Waiver.Status.approved, Waiver.Status.denied])
        waiver_type = itertools.cycle([Waiver.Type.partial, Waiver.Type.full])
        waiver_category = itertools.cycle([Waiver.Category.language, Waiver.Category.six_eight, Waiver.Category.fairshare])

        for bid in list(Bid.objects.all().order_by('?')[:20]):
            Waiver.objects.create(type=next(waiver_type), category=next(waiver_category), user=bid.user, position=bid.position, bid=bid)

        # Randomly alter waiver statuses
        for waiver in list(Waiver.objects.all().order_by('?')):
            waiver.status = next(waiver_status)
            self.logger.info(f"Setting waiver status: {waiver}")
            waiver.save()

        self.logger.info("Done seeding waivers")
