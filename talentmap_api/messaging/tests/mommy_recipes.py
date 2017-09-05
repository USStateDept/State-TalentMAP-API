from model_mommy import mommy

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification


def owned_notification():
    return mommy.make(Notification, owner=UserProfile.objects.last())
