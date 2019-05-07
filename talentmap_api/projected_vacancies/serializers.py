from django.http import QueryDict

from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite
import talentmap_api.fsbid.services as services

class ProjectedVacancySerializer(PrefetchedSerializer):

    position = serializers.SerializerMethodField()

    class Meta:
        model = ProjectedVacancyFavorite
        fields = ["position"]

    def get_position(self, obj):
      return services.get_projected_vacancies(QueryDict("position_number=f{obj.position_number}"))
