import rest_framework_filters as filters

import talentmap_api.fsbid.services.projected_vacancies as pv_services

import logging
logger = logging.getLogger(__name__)

# Filter handles not having database tables backing the model
class ProjectedVacancyFilter():
    declared_filters = [
        "projectedVacancy",
        "is_available_in_bidseason",
        "position__skill__code__in",
        "position__grade__code__in",
        "position__bureau__code__in",
        "position__post__tour_of_duty__code__in",
        "language_codes",
        "position__post__differential_rate__in",
        "position__post__danger_pay__in",
    ]

    use_api = True

    # Used when saving a search to determine the number of records returned
    def get_count(query, jwt_token):
        return pv_services.get_projected_vacancies_count(query, jwt_token)

    class Meta:
        fields = "__all__"
