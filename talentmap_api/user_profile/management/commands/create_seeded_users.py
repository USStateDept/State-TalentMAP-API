from django.core.management.base import BaseCommand

import logging

from django.contrib.auth.models import User
from django.utils import timezone
from talentmap_api.common.common_helpers import get_group_by_name, get_permission_by_name
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a set of users for testing purposes and seeds their skill codes and grades'
    logger = logging.getLogger(__name__)

    # username, email, password, firstname, lastname, is_ao, is_cdo, extra_permission_groups
    USERS = [
        ("guest", "guest@state.gov", "guestpassword", "Guest", "McGuestson", False, False, ["bidder"]),
        ("admin", "admin@talentmap.us", "admin", "Administrator", "TalentMAP", False, False, ["superuser"]),
        ("doej", "doej@talentmap.us", "password", "John", "Doe", False, False, ["bidder"]),
        ("townpostj", "townpostj@state.gov", "password", "Jenny", "Townpost", False, False, ["glossary_editors"]),
        ("batisak", "batisak@state.gov", "password", "Kara", "Batisak", False, False, ["bidder"]),
        ("rehmant", "rehmant@state.gov", "password", "Tarek", "Rehman", False, False, ["bidder", "helppage_editor"]),
        ("shadtrachl", "shadtrachl@state.gov", "password", "Leah", "Shadtrach", False, True, ["bidder", "cdo"]),
        ("woodwardw", "woodwardw@state.gov", "password", "Wendy", "Woodward", True, False, ["bidder"]),
        ("velezp", "velezp@state.gov", "password", "Preston", "Velez", False, True, ["bidder"]),
        ("lincolna", "lincolna@state.gov", "password", "Abigail", "Lincoln", True, True, ["bidder", "cdo"]),
    ]

    def handle(self, *args, **options):
        for data in self.USERS:
            try:
                try:
                    user = User.objects.get(username=data[0])
                except User.DoesNotExist:
                    user = User.objects.create_user(data[0], data[1], data[2])
                user.first_name = data[3]
                user.last_name = data[4]
                user.save()

                profile = UserProfile.objects.get(user=user)
                profile.emp_id = f"{user.first_name}_{user.last_name}"
                profile.save()

                for group in data[7]:
                    get_group_by_name(group).user_set.add(user)

                self.logger.info(f"Successfully created {user.first_name} {user.last_name}, {user.username} ({user.email})\n\tGroups: {user.groups.all()}")
            except Exception as e:
                self.logger.info(f"Could not create {data}, {e}")
