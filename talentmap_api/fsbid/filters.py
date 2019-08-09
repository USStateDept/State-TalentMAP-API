import rest_framework_filters as filters

import talentmap_api.fsbid.services as services

import logging
logger = logging.getLogger(__name__)


# Filter handles not having database tables backing the model
class ProjectedVacancyFilter():
    declared_filters = [
        "projectedVacancy",
        "is_available_in_bidseason",
        "skill__code__in",
        "grade__code__in",
        "bureau__code__in",
        "post__tour_of_duty__code__in",
        "language_codes",
        "post__differential_rate__in",
        "post__danger_pay__in",
    ]

    use_api = True

    # Used when saving a search to determine the number of records returned
    def get_queryset(query):
        def count(self):
            return services.get_projected_vacancies_count(query, request.META['HTTP_JWT'])

        return type('', (object,), {'count': count})()

    class Meta:
        fields = "__all__"
