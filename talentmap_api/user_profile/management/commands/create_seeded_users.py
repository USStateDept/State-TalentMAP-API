from django.core.management.base import BaseCommand

import logging
import random

from django.contrib.auth.models import User
from talentmap_api.common.common_helpers import get_permission_by_name
from talentmap_api.position.models import Position, Skill, Grade
from talentmap_api.user_profile.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a set of users for testing purposes and seeds their skill codes and grades'
    logger = logging.getLogger('console')

    USERS = [
        ("guest", "guest@state.gov", "guestpassword", "Guest", "McGuestson",),
        ("admin", "admin@talentmap.us", "admin", "Administrator", "TalentMAP",),
        ("townpostj", "townpostj@state.gov", "password", "Jenny", "Townpost",),
        ("batisak", "batisak@state.gov", "password", "Kara", "Batisak",),
        ("rehmant", "rehmant@state.gov", "password", "Tarek", "Rehman",)
    ]

    def handle(self, *args, **options):
        skills = list(set(Position.objects.all().values_list('skill', flat=True)))
        grades = list(set(Position.objects.all().values_list('grade', flat=True)))
        bureaus = list(set(Position.objects.all().values_list('bureau__code', flat=True)))
        random.shuffle(skills)
        random.shuffle(grades)
        random.shuffle(bureaus)
        for data in self.USERS:
            try:
                user = User.objects.create_user(data[0], data[1], data[2])
                user.first_name = data[3]
                user.last_name = data[4]
                user.save()

                profile = UserProfile.objects.get(user=user)
                profile.skill_code = Skill.objects.get(id=skills.pop())
                profile.grade = Grade.objects.get(id=grades.pop())
                profile.save()

                permission = get_permission_by_name(f'organization.can_highlight_positions_{bureaus.pop()}')
                user.user_permissions.add(permission)

                self.logger.info(f"Successfully created {user.first_name} {user.last_name}, {user.username} ({user.email})\n\tSkill: {profile.skill_code}\n\tGrade: {profile.grade}\n\tPermission: {permission}")
            except Exception as e:
                self.logger.info(f"Could not create {data}, {e}")
