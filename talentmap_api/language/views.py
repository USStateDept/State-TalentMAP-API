from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin

from talentmap_api.language.models import Language, Proficiency, Qualification, Waiver
from talentmap_api.language.serializers import LanguageSerializer, LanguageProficiencySerializer, LanguageQualificationSerializer, LanguageQualificationWritableSerializer, WaiverSerializer, WaiverWritableSerializer
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
        return get_prefetched_filtered_queryset(Language)


class LanguageWaiverHistoryView(FieldLimitableSerializerMixin,
                                GenericViewSet,
                                mixins.ListModelMixin):
    '''
    list:
    Lists all of the language's waivers
    '''

    serializer_class = WaiverSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))
    filter_class = WaiverFilter

    def get_queryset(self):
        # Get the language based on the PK from the url
        language = get_object_or_404(Language, pk=self.request.parser_context.get("kwargs").get("pk"))
        # Get the position's assignments
        queryset = language.waivers.all()
        self.serializer_class.prefetch_model(Waiver, queryset)
        return queryset


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
        return get_prefetched_filtered_queryset(Proficiency)


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
        return get_prefetched_filtered_queryset(Qualification)


class WaiverView(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.CreateModelMixin,
                 ActionDependentSerializerMixin,
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
    serializers = {
        "default": WaiverSerializer,
        "create": WaiverWritableSerializer
    }

    serializer_class = WaiverSerializer
    filter_class = WaiverFilter
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=UserProfile.objects.get(user=self.request.user))

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).language_waivers.all()
        queryset = self.serializer_class.prefetch_model(Waiver, queryset)
        return queryset
