import rest_framework_filters as filters

import talentmap_api.fsbid.services.projected_vacancies as pv_services
import talentmap_api.fsbid.services.available_positions as ap_services

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
        "position__post__in",
        "is_overseas",
        "is_domestic",
        "q",
        "org_has_groups",
    ]

    use_api = True

    # Used when saving a search to determine the number of records returned
    def get_count(query, jwt_token):
        return pv_services.get_projected_vacancies_count(query, jwt_token)

    class Meta:
        fields = "__all__"


class AvailablePositionsFilter():
    declared_filters = [
        "is_available_in_bidcycle",
        "position__skill__code__in",
        "position__grade__code__in",
        "position__bureau__code__in",
        "is_domestic",
        "position__post__in",
        "position__post__tour_of_duty__code__in",
        "position__post__differential_rate__in",
        "language_codes",
        "position__post__danger_pay__in",
        "is_available_in_current_bidcycle",
        "q",
        "position__post__in",
        "is_overseas",
        "org_has_groups",
    ]

    use_api = True

    # Used when saving a search to determine the number of records returned
    def get_count(query, jwt_token):
        pass
        # TODO - once using available_positions, re-enable this and close TM-1314
        #return ap_services.get_available_positions_count(query, jwt_token)

    class Meta:
        fields = "__all__"
