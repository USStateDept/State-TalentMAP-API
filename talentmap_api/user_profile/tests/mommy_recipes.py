from model_mommy import mommy

from talentmap_api.user_profile.models import UserProfile, SavedSearch


def owned_saved_search():
    # This must have a valid endpoint
    return mommy.make(SavedSearch, owner=UserProfile.objects.last(), endpoint='/api/v1/position/')


def client_for_profile():
    user = mommy.make('auth.User')
    user.profile.cdo = UserProfile.objects.get(user__username="authorized_user")
    user.profile.date_of_birth = "1975-01-01T00:00:00Z"
    user.profile.save()

    return user.profile
