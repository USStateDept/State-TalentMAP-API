from django.core.management.base import BaseCommand

import logging
import datetime

from django.contrib.auth.models import User
from talentmap_api.common.common_helpers import get_group_by_name
from talentmap_api.position.models import Position, Assignment
from talentmap_api.organization.models import TourOfDuty, Country
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a set of users for testing purposes and seeds their skill codes and grades'
    logger = logging.getLogger('console')

    # username, email, password, firstname, lastname, is_ao, is_cdo
    USERS = [
        ("guest", "guest@state.gov", "guestpassword", "Guest", "McGuestson", False, False),
        ("admin", "admin@talentmap.us", "admin", "Administrator", "TalentMAP", False, False),
        ("doej", "doej@talentmap.us", "password", "John", "Doe", False, False),
        ("townpostj", "townpostj@state.gov", "password", "Jenny", "Townpost", False, False),
        ("batisak", "batisak@state.gov", "password", "Kara", "Batisak", False, False),
        ("rehmant", "rehmant@state.gov", "password", "Tarek", "Rehman", False, False),
        ("shadtrachl", "shadtrachl@state.gov", "password", "Leah", "Shadtrach", False, True),
        ("woodwardw", "woodwardw@state.gov", "password", "Wendy", "Woodward", True, False)
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
                profile.date_of_birth = "1975-01-01"
                profile.phone_number = "555-555-5555"
                profile.save()

                assignment = Assignment.objects.create(user=profile, position=position, tour_of_duty=TourOfDuty.objects.all().first(), start_date=datetime.datetime.now().date().strftime('%Y-%m-%d'), status="active")

                # Add the user to the editing group for their position
                group = get_group_by_name(f"post_editors_{position.post.id}")
                group.user_set.add(user)

                if data[5]:
                    group = get_group_by_name(f"bureau_ao")
                    group.user_set.add(user)

                    group = get_group_by_name(f"bureau_ao_150000")
                    group.user_set.add(user)

                if data[6]:
                    UserProfile.objects.exclude(id=profile.id).update(cdo=profile)

                self.logger.info(f"Successfully created {user.first_name} {user.last_name}, {user.username} ({user.email})\n\tSkill: {profile.skills}\n\tGrade: {profile.grade}\n\tGroups: {user.groups.all()}\n\tAssignment: {assignment}")
            except Exception as e:
                self.logger.info(f"Could not create {data}, {e}")
