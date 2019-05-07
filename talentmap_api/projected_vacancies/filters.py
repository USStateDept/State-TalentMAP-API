import rest_framework_filters as filters

from talentmap_api.common.filters import ALL_TEXT_LOOKUPS

from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

class ProjectedVacancyFilter(filters.FilterSet):

  class Meta:
        model = ProjectedVacancyFavorite
        fields = {
            "position_number": ALL_TEXT_LOOKUPS
        }

