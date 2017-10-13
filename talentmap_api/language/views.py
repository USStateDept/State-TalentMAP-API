from rest_framework import mixins
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin

from talentmap_api.language.models import Language, Proficiency, Qualification, Waiver
from talentmap_api.language.serializers import LanguageSerializer, LanguageProficiencySerializer, LanguageQualificationSerializer, LanguageQualificationWritableSerializer, WaiverSerializer
from talentmap_api.language.filters import LanguageFilter, ProficiencyFilter, QualificationFilter, WaiverFilter

from talentmap_api.user_profile.models import UserProfile


class LanguageListView(FieldLimitableSerializerMixin,
                       ReadOnlyModelViewSet):
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


class LanguageProficiencyListView(FieldLimitableSerializerMixin,
                                  ReadOnlyModelViewSet):
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


class LanguageQualificationListView(FieldLimitableSerializerMixin,
                                    mixins.RetrieveModelMixin,
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


class WaiverView(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.CreateModelMixin,
                 GenericViewSet):
    '''
    list:
    Lists all of the user's waivers
    retrieve:
    Returns the specified waiver
    partial_update:
    Update the specified waiver
    create:
    Create a new waiver request
    '''
    serializer_class = WaiverSerializer
    filter_class = WaiverFilter
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=UserProfile.objects.get(user=self.request.user))

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).language_waivers.all()
        queryset = self.serializer_class.prefetch_model(Waiver, queryset)
        return queryset
