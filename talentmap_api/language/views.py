from rest_framework import mixins
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.mixins import ActionDependentSerializerMixin

from talentmap_api.language.models import Language, Proficiency, Qualification
from talentmap_api.language.serializers import LanguageSerializer, LanguageProficiencySerializer, LanguageQualificationSerializer, LanguageQualificationWritableSerializer
from talentmap_api.language.filters import LanguageFilter, ProficiencyFilter, QualificationFilter


class LanguageListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given language.

    list:
    Return a list of all languages.
    """

    serializer_class = LanguageSerializer
    filter_class = LanguageFilter

    def get_queryset(self):
        return Language.objects.all()


class LanguageProficiencyListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given proficiency.

    list:
    Return a list of all proficiencies.
    """

    serializer_class = LanguageProficiencySerializer
    filter_class = ProficiencyFilter

    def get_queryset(self):
        return Proficiency.objects.all()


class LanguageQualificationListView(mixins.RetrieveModelMixin,
                                    mixins.ListModelMixin,
                                    mixins.CreateModelMixin,
                                    ActionDependentSerializerMixin,
                                    GenericViewSet):
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
        queryset = Qualification.objects.all()
        queryset = self.serializer_class.prefetch_model(Qualification, queryset)
        return queryset
