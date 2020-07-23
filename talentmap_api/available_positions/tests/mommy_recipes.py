from model_mommy.recipe import Recipe

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.available_positions.models import AvailablePositionFavorite

available_position_favorite = Recipe(
    AvailablePositionFavorite,
    cp_id="1",
    user=UserProfile.objects.last(),
)
