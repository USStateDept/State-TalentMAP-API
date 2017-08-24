from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework import mixins
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from talentmap_api.position.models import Position, Grade, Skill, CapsuleDescription
from talentmap_api.position.filters import PositionFilter, GradeFilter, SkillFilter, CapsuleDescriptionFilter
from talentmap_api.position.serializers import PositionSerializer, GradeSerializer, SkillSerializer, CapsuleDescriptionSerializer

from talentmap_api.user_profile.models import UserProfile


class PositionListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given position.

    list:
    Return a list of all positions.
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter

    def get_queryset(self):
        queryset = Position.objects.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class PositionFavoriteListView(ReadOnlyModelViewSet):
    """
    list:
    Return a list of all of the user's favorite positions.
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).favorite_positions.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class CapsuleDescriptionView(GenericViewSet,
                             mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin):
    '''
    create:
    Creates a new capsule description

    partial_update:
    Edits a saved capsule description

    retrieve:
    Retrieves a specific capsule description

    list:
    Lists all capsule descriptions

    destroy:
    Deletes a specified capsule description
    '''

    serializer_class = CapsuleDescriptionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = CapsuleDescriptionFilter

    def perform_create(self, serializer):
        serializer.save(last_editing_user=self.request.user.profile)

    def perform_update(self, serializer):
        serializer.save(last_editing_user=self.request.user.profile)

    def get_queryset(self):
        queryset = CapsuleDescription.objects.all()
        self.serializer_class.prefetch_model(CapsuleDescription, queryset)
        return queryset


class GradeListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given grade.

    list:
    Return a list of all grades.
    """

    serializer_class = GradeSerializer
    filter_class = GradeFilter

    def get_queryset(self):
        queryset = Grade.objects.all()
        queryset = self.serializer_class.prefetch_model(Grade, queryset)
        return queryset


class SkillListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given skill.

    list:
    Return a list of all skills.
    """

    serializer_class = SkillSerializer
    filter_class = SkillFilter

    def get_queryset(self):
        queryset = Skill.objects.all()
        queryset = self.serializer_class.prefetch_model(Skill, queryset)
        return queryset
