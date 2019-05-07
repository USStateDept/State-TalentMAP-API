from model_mommy import mommy
from model_mommy.recipe import Recipe, seq, foreign_key

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

projected_vacancy_favorite = Recipe(
    ProjectedVacancyFavorite,
    position_number=1,
    user=UserProfile.objects.last(),
)