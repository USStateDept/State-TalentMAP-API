from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification


def owned_notification():
    return mommy.make(Notification, owner=UserProfile.objects.last())
