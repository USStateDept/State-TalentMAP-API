from django.core.management.base import BaseCommand

import logging
import datetime

from django.contrib.auth.models import User
from talentmap_api.common.common_helpers import get_group_by_name
from talentmap_api.position.models import Position, Assignment
from talentmap_api.organization.models import TourOfDuty
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a set of users for testing purposes and seeds their skill codes and grades'
    logger = logging.getLogger('console')

    USERS = [
        ("guest", "guest@state.gov", "guestpassword", "Guest", "McGuestson", False),
        ("admin", "admin@talentmap.us", "admin", "Administrator", "TalentMAP", False),
        ("townpostj", "townpostj@state.gov", "password", "Jenny", "Townpost", False),
        ("batisak", "batisak@state.gov", "password", "Kara", "Batisak", False),
        ("rehmant", "rehmant@state.gov", "password", "Tarek", "Rehman", True)
    ]

    def handle(self, *args, **options):
        positions = list(set(Position.objects.filter(bureau__isnull=False).order_by('bureau__code').distinct('bureau__code').values_list('id', flat=True)))
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
                profile.skill_code = position.skill
                profile.grade = position.grade
                profile.save()

                assignment = Assignment.objects.create(user=profile, position=position, tour_of_duty=TourOfDuty.objects.all().first(), start_date=datetime.datetime.now().date().strftime('%Y-%m-%d'))

                # Add the user to the editing group for their position
                group = get_group_by_name(f"post_editors_{position.post.id}")
                group.user_set.add(user)

                if data[5]:
                    group = get_group_by_name(f"bureau_ao")
                    group.user_set.add(user)

                    group = get_group_by_name(f"bureau_ao_{position.bureau.code}")
                    group.user_set.add(user)

                self.logger.info(f"Successfully created {user.first_name} {user.last_name}, {user.username} ({user.email})\n\tSkill: {profile.skill_code}\n\tGrade: {profile.grade}\n\tGroups: {user.groups.all()}\n\tAssignment: {assignment}")
            except Exception as e:
                self.logger.info(f"Could not create {data}, {e}")
