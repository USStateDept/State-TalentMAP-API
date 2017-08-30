from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile, SavedSearch


def owned_saved_search():
    # This must have a valid endpoint
    return mommy.make(SavedSearch, owner=UserProfile.objects.last(), endpoint='/api/v1/position/')
