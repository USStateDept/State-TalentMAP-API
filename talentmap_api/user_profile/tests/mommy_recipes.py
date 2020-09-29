from model_mommy import mommy

from talentmap_api.user_profile.models import UserProfile, SavedSearch


def owned_saved_search():
    # This must have a valid endpoint
    return mommy.make(SavedSearch, owner=UserProfile.objects.last(), endpoint='/api/v1/fsbid/available_positions/')
