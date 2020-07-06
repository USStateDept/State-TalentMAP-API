from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.cache.views import CachedViewSet
from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin
from talentmap_api.language.models import Language, Proficiency, Qualification
from talentmap_api.language.serializers import LanguageSerializer, LanguageProficiencySerializer, LanguageQualificationSerializer, LanguageQualificationWritableSerializer
from talentmap_api.language.filters import LanguageFilter, ProficiencyFilter, QualificationFilter


class LanguageListView(FieldLimitableSerializerMixin,
                       CachedViewSet):
    """
    retrieve:
    Return the given language.

    list:
    Return a list of all languages.
    """

    serializer_class = LanguageSerializer
    filter_class = LanguageFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Language, self.serializer_class)


class LanguageProficiencyListView(FieldLimitableSerializerMixin,
                                  CachedViewSet):
    """
    retrieve:
    Return the given proficiency.

    list:
    Return a list of all proficiencies.
    """

    serializer_class = LanguageProficiencySerializer
    filter_class = ProficiencyFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Proficiency, self.serializer_class)


class LanguageQualificationListView(FieldLimitableSerializerMixin,
                                    mixins.CreateModelMixin,
                                    ActionDependentSerializerMixin,
                                    CachedViewSet):
    """
    retrieve:
    Return the given qualification.

    list:
    Return a list of all qualifications.

    create:
    Add a language qualification if it does not exist.
    """

    serializers = {
        "default": LanguageQualificationSerializer,
        "create": LanguageQualificationWritableSerializer
    }

    serializer_class = LanguageQualificationSerializer
    filter_class = QualificationFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return get_prefetched_filtered_queryset(Qualification, self.serializer_class)
