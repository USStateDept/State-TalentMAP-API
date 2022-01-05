from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

import logging
import random
import itertools

from dateutils import relativedelta

from django.contrib.auth.models import User

from talentmap_api.glossary.models import GlossaryEntry
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
        call_command("create_base_permissions")
        call_command("create_obc")
        call_command("create_seeded_users")
        today = timezone.now()

        profile = UserProfile.objects.get(user__username="doej")
        self.logger.info("Created.")

        min_client_count=20

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

            user.profile.emp_id = f"{fname}_{lname}"

            user.profile.save()

        self.logger.info("Updating string representations...")
        call_command("update_string_representations")
