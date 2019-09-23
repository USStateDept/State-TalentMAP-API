from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

import logging
import random
import itertools

from dateutils import relativedelta

from django.contrib.auth.models import User

from talentmap_api.bidding.models import BidCycle, Bid, Waiver, StatusSurvey, CyclePosition
from talentmap_api.position.models import Position
from talentmap_api.glossary.models import GlossaryEntry
from talentmap_api.messaging.models import Task
from talentmap_api.organization.models import TourOfDuty
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates demo environment - seeded users, default bidcycle'
    logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

        self.first_names = [
            "Arthur",
            "Rusty",
            "Russell",
            "Edmond",
            "Nathanial",
            "King",
            "Aron",
            "Ward",
            "Brendan",
            "Lesley",
            "Waldo",
            "Foster",
            "Will",
            "Arden",
            "Mose",
            "Major",
            "Patrick",
            "Daryl",
            "Grover",
            "Cristobal",
            "Israel",
            "Genaro",
            "Fidel",
            "Lawerence",
            "Jamel",
            "Harley",
            "Clair",
            "Ben",
            "Miguel",
            "Cleveland",
            "Weston",
            "Zackary",
            "Vance",
            "Luis",
            "Jamar",
            "Milan",
            "Ryan",
            "Duncan",
            "Mitchell",
            "Minh",
            "Garret",
            "Wade",
            "Marco",
            "Antwan",
            "Francisco",
            "Damian",
            "Owen",
            "Neville",
            "Travis",
            "Gilberto",
            "Lisha",
            "Serina",
            "Damaris",
            "Trisha",
            "Rhonda",
            "Marnie",
            "Margot",
            "Gita",
            "Tam",
            "Retha",
            "Ulrike",
            "Adina",
            "Halina",
            "Noelle",
            "Britni",
            "Sherita",
            "Vanetta",
            "Chantal",
            "Nelle",
            "Chasity",
            "Clarita",
            "Oralee",
            "Katharyn",
            "Daria",
            "Reita",
            "Shelba",
            "Viki",
            "Susanna",
            "Marlene",
            "Dottie",
            "Mertie",
            "Tran",
            "Ossie",
            "Tessa",
            "Christen",
            "Sara",
            "Dorene",
            "Jackelyn",
            "Rosina",
            "Reda",
            "Tarah",
            "Katharina",
            "Piedad",
            "Mila",
            "Merry",
            "Shila",
            "Genesis",
            "Crystle",
            "Roxy",
            "Zula",
        ]

        self.last_names = [
            "Koehl",
            "Albee",
            "Prince",
            "Dumond",
            "Thoreson",
            "Currie",
            "Ference",
            "Hippe",
            "Schroyer",
            "Seabolt",
            "Mosqueda",
            "Cowley",
            "Ebron",
            "Cope",
            "Legette",
            "Ranallo",
            "Sawtelle",
            "Walko",
            "Cieslak",
            "Barhorst",
            "Barrio",
            "Reddick",
            "Torre",
            "Mattison",
            "Rath",
            "Collins",
            "Sharples",
            "Mayhugh",
            "Ange",
            "Pershall",
            "Ostrem",
            "Tomberlin",
            "Gammel",
            "Overman",
            "Filice",
            "Fadden",
            "Goldner",
            "Kirkman",
            "Then",
            "Gottlieb",
            "Talley",
            "Haight",
            "Damelio",
            "Ratcliffe",
            "Lazarus",
            "Borrelli",
            "Ross",
            "Holstein",
            "Bradish",
            "Trumbauer",
            "Hinojos",
            "Harlan",
            "Menzie",
            "Mccourt",
            "Sipos",
            "Nadeau",
            "Santoro",
            "Cheadle",
            "Littlefield",
            "Yerger",
            "Hefley",
            "Mcguffey",
            "Oliveira",
            "Mckinnon",
            "Ausmus",
            "Rentz",
            "Enlow",
            "Mcniel",
            "Deville",
            "Funkhouser",
            "Brinegar",
            "Randel",
            "Bunt",
            "Heitmann",
            "Bierbaum",
            "Dias",
            "Coplan",
            "Linsey",
            "Linares",
            "Rockett",
            "Neuman",
            "Ospina",
            "Mook",
            "Finkel",
            "Hardy",
            "Guerrero",
            "Lyon",
            "Glazer",
            "Ricardo",
            "Barkley",
            "Rayo",
            "Mcmann",
            "Levey",
            "Billingslea",
            "Embrey",
            "Stransky",
            "Simone",
            "Hilson",
            "Kelling",
            "Mcculloch",
        ]

    def handle(self, *args, **options):
        call_command("create_seeded_users")
        CyclePosition.objects.all().delete()
        BidCycle.objects.all().delete()
        today = timezone.now()
        # Create bidcycle with all positions
        bc = BidCycle.objects.create(active=True,
                                     name=f"Demo BidCycle {timezone.now()}",
                                     cycle_start_date=today - relativedelta(months=3),
                                     cycle_deadline_date=today + relativedelta(months=1),
                                     cycle_end_date=today + relativedelta(months=3))

        
        for pos in Position.objects.all():
            CyclePosition.objects.create(bidcycle=bc, position=pos, posted_date=today, ted=today)

        self.logger.info(f"Created demo bidcycle with all positions: {bc.name}")

        self.logger.info(f"Setting all position posted dates, and statuses")
        Position.objects.all().update(posted_date="2006-05-20T15:00:00Z")

        profile = UserProfile.objects.get(user__username="doej")
        self.logger.info("Created.")

        self.logger.info(f"Seeding bids for all users...")
        persona_users = UserProfile.objects.exclude(user__username__in=["admin", "doej", "guest", "woodwardw"]).all()
        valid_users = itertools.cycle(list(persona_users))
        reviewer = UserProfile.objects.get(user__username="woodwardw")

        # Remove any previous SII surveys
        StatusSurvey.objects.all().delete()

        # Create SII surveys
        for user in list(persona_users):
            StatusSurvey.objects.create(user=user, bidcycle=bc)

        # Remove any existing bids
        Bid.objects.all().delete()

        # Create 40 bids, with competition
        positions = list(CyclePosition.objects.filter(position__bureau__code="150000").order_by('?'))  # Our AO persona gets all the bids
        for _ in range(0, 20):
            position = positions.pop()
            Bid.objects.create(position=position, bidcycle=bc, user=next(valid_users), reviewer=reviewer)
            Bid.objects.create(position=position, bidcycle=bc, user=next(valid_users), reviewer=reviewer)
        self.logger.info(f"Seeded bids, randomly altering statuses...")
        # Assign random bids statuses
        statuses = itertools.cycle([Bid.Status.submitted, Bid.Status.handshake_offered])
        for bid in list(Bid.objects.all().order_by('?')[:20]):
            bid.status = next(statuses)
            setattr(bid, f"{bid.status}_date", timezone.now())
            self.logger.info(f"Setting bid status: {bid}")
            bid.save()

            if bid.status == Bid.Status.handshake_offered or bid.status == Bid.Status.handshake_accepted:
                bid.position.status = "Handshake"
                bid.position.status_code = "HS"
                bid.position.save()

        # Move one bid through the entire process
        bid = Bid.objects.exclude(user__user__username='woodwardw').filter(status=Bid.Status.submitted).first()
        self.logger.info(f"Walking through bid process with {bid.id} {bid}")
        bid.status = Bid.Status.handshake_offered
        bid.handshake_offered_date = timezone.now()
        bid.save()

        bid.status = Bid.Status.handshake_accepted
        bid.handshake_accepted_date = timezone.now()
        bid.save()

        bid.status = Bid.Status.in_panel
        bid.in_panel_date = timezone.now()
        bid.scheduled_panel_date = "2017-12-25T00:00:00Z"
        bid.save()

        # Reschedule the bid
        bid.scheduled_panel_date = "2018-01-20T00:00:00Z"
        bid.save()

        bid.status = Bid.Status.approved
        bid.approved_date = timezone.now()
        bid.save()

        self.logger.info("Done initializing bids")

        self.logger.info("Seeding waiver requests...")
        Waiver.objects.all().delete()

        waiver_status = itertools.cycle([Waiver.Status.requested, Waiver.Status.approved, Waiver.Status.denied])
        waiver_type = itertools.cycle([Waiver.Type.partial, Waiver.Type.full])
        waiver_category = itertools.cycle([Waiver.Category.language, Waiver.Category.six_eight, Waiver.Category.fairshare])

        for bid in list(Bid.objects.all().order_by('?')[:20]):
            Waiver.objects.create(type=next(waiver_type), category=next(waiver_category), user=bid.user, position=bid.position.position, bid=bid)

        # Randomly alter waiver statuses
        for waiver in list(Waiver.objects.all().order_by('?')):
            waiver.status = next(waiver_status)
            self.logger.info(f"Setting waiver status: {waiver}")
            waiver.save()

        self.logger.info("Done seeding waivers")

        self.logger.info("Create some glossary entries")
        GlossaryEntry.objects.get_or_create(title="Waiver", definition="A waiver grants an exclusion to a position's requirements")
        GlossaryEntry.objects.get_or_create(title="Position", definition="A position represents a particular job", link="http://www.google.com")

        self.logger.info("Creating some tasks")
        for user in list(persona_users):
            Task.objects.create(owner=user, content="Demo Task", title="Demo task", tags=["todo"], date_due="2018-12-25T00:00:00Z")

        min_position_count = 6000
        min_client_count = 600

        self.logger.info(f"Padding positions to {min_position_count}")
        count = Position.objects.count()
        while count < min_position_count:
            for position in list(Position.objects.all()):
                # Duplicate the description
                description = position.description
                description.id = None
                description.save()

                # Duplicate position
                position.id = None
                position.description = description
                position.save()

                # Add a new CyclePosition for the position
                CyclePosition.objects.create(bidcycle=bc, position=position, posted_date=today, ted=today)

                count = count + 1
                if count >= min_position_count:
                    break

            self.logger.info(f"Position count: {Position.objects.count()}")

        self.logger.info(f"Padding clients to {min_client_count}")
        sysrandom = random.SystemRandom()
        for i in range(0, min_client_count - User.objects.count()):
            # Create a new user
            fname = sysrandom.choice(self.first_names)
            lname = sysrandom.choice(self.last_names)
            username = f"{lname}{fname[0]}_{i}"
            user = User.objects.create_user(f"{username}", f"{username}@state.gov", "password")
            user.first_name = fname
            user.last_name = lname
            user.save()

            user.profile.cdo = User.objects.get(username="shadtrachl").profile
            user.profile.emp_id = f"{fname}_{lname}"

            user.profile.save()

        self.logger.info("Updating string representations...")
        call_command("update_string_representations")
