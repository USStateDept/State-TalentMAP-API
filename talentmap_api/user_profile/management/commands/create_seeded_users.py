from django.core.management.base import BaseCommand

import logging

from django.contrib.auth.models import User
from django.utils import timezone
from talentmap_api.common.common_helpers import get_group_by_name
from talentmap_api.position.models import Position, Assignment
from talentmap_api.organization.models import TourOfDuty, Country
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a set of users for testing purposes and seeds their skill codes and grades'
    logger = logging.getLogger(__name__)

    # username, email, password, firstname, lastname, is_ao, is_cdo, extra_permission_groups
    USERS = [
        ("guest", "guest@state.gov", "guestpassword", "Guest", "McGuestson", False, False, []),
        ("admin", "admin@talentmap.us", "admin", "Administrator", "TalentMAP", False, False, ["feedback_editors"]),
        ("doej", "doej@talentmap.us", "password", "John", "Doe", False, False, []),
        ("townpostj", "townpostj@state.gov", "password", "Jenny", "Townpost", False, False, ["glossary_editors"]),
        ("batisak", "batisak@state.gov", "password", "Kara", "Batisak", False, False, []),
        ("rehmant", "rehmant@state.gov", "password", "Tarek", "Rehman", False, False, []),
        ("shadtrachl", "shadtrachl@state.gov", "password", "Leah", "Shadtrach", False, True, []),
        ("woodwardw", "woodwardw@state.gov", "password", "Wendy", "Woodward", True, False, ["feedback_editors"])
    ]

    def handle(self, *args, **options):
        positions = list(set(Position.objects.filter(bureau__code="150000").values_list('id', flat=True)))
        positions = positions + list(set(Position.objects.filter(bureau__isnull=False).exclude(bureau__code="150000").order_by('bureau__code').values_list('id', flat=True)))
        for data in self.USERS:
            try:
                try:
                    user = User.objects.get(username=data[0])
                except User.DoesNotExist:
                    user = User.objects.create_user(data[0], data[1], data[2])
                user.first_name = data[3]
                user.last_name = data[4]
                user.save()

                position = Position.objects.get(id=positions.pop())
                profile = UserProfile.objects.get(user=user)
                profile.skills.add(position.skill)
                profile.grade = position.grade
                profile.primary_nationality = Country.objects.get(code="USA")
                profile.date_of_birth = "1975-01-01T00:00:00Z"
                profile.phone_number = "555-555-5555"
                profile.emp_id = f"{first_name}_{last_name}"
                profile.save()

                assignment = Assignment.objects.create(user=profile, position=position, tour_of_duty=TourOfDuty.objects.all().first(), start_date=timezone.now(), status="active", bid_approval_date="1975-01-01T00:00:00Z")

                # Add user to the bidder group
                group = get_group_by_name("bidder")
                group.user_set.add(user)

                # Add the user to the editing group for their position
                group = get_group_by_name(f"post_editors:{position.post.id}")
                group.user_set.add(user)

                if data[5]:
                    group = get_group_by_name(f"bureau_ao")
                    group.user_set.add(user)

                    group = get_group_by_name(f"bureau_ao:150000")
                    group.user_set.add(user)

                if data[6]:
                    UserProfile.objects.exclude(id=profile.id).update(cdo=profile)

                for group in data[7]:
                    get_group_by_name(group).user_set.add(user)

                self.logger.info(f"Successfully created {user.first_name} {user.last_name}, {user.username} ({user.email})\n\tSkill: {profile.skills}\n\tGrade: {profile.grade}\n\tGroups: {user.groups.all()}\n\tAssignment: {assignment}")
            except Exception as e:
                self.logger.info(f"Could not create {data}, {e}")
