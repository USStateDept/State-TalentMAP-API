from django.db.models import Count

from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin
from talentmap_api.common.common_helpers import has_permission_or_403

from talentmap_api.position.models import Position, Grade, Skill, CapsuleDescription, Classification
from talentmap_api.position.filters import PositionFilter, GradeFilter, SkillFilter, CapsuleDescriptionFilter
from talentmap_api.position.serializers import PositionSerializer, PositionWritableSerializer, GradeSerializer, SkillSerializer, CapsuleDescriptionSerializer, ClassificationSerializer

from talentmap_api.user_profile.models import UserProfile


class PositionListView(FieldLimitableSerializerMixin,
                       ActionDependentSerializerMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       GenericViewSet):
    """
    retrieve:
    Return the given position.

    list:
    Return a list of all positions.

    partial_update:
    Update a position
    """

    serializers = {
        "default": PositionSerializer,
        "partial_update": PositionWritableSerializer,
    }

    serializer_class = PositionSerializer
    filter_class = PositionFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Position.objects.all()
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class PositionFavoriteListView(FieldLimitableSerializerMixin,
                               ReadOnlyModelViewSet):
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


class PositionHighlightListView(FieldLimitableSerializerMixin,
                                ReadOnlyModelViewSet):
    """
    list:
    Return a list of all currently highlighted positions
    """

    serializer_class = PositionSerializer
    filter_class = PositionFilter

    def get_queryset(self):
        queryset = Position.objects.annotate(highlight_count=Count('highlighted_by_org')).filter(highlight_count__gt=0)
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        return queryset


class PositionFavoriteActionView(APIView):
    '''
    Controls the favorite status of a position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the position is a favorite

        Returns 204 if the position is a favorite, otherwise, 404
        '''
        if UserProfile.objects.get(user=self.request.user).favorite_positions.filter(id=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the position as a favorite
        '''
        UserProfile.objects.get(user=self.request.user).favorite_positions.add(Position.objects.get(id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from favorites
        '''
        UserProfile.objects.get(user=self.request.user).favorite_positions.remove(Position.objects.get(id=pk))
        return Response(status=status.HTTP_204_NO_CONTENT)


class PositionHighlightActionView(APIView):
    '''
    Controls the highlighted status of a position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the position is highlighted

        Returns 204 if the position is highlighted, otherwise, 404
        '''
        if Position.objects.get(id=pk).highlighted_by_org.count() > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the position as highlighted by the position's bureau
        '''
        position = Position.objects.get(id=pk)

        # Check for the bureau permission on the accessing user
        has_permission_or_403(self.request.user, f"organization.can_highlight_positions_{position.bureau.code}")
        position.bureau.highlighted_positions.add(position)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from highlighted positions
        '''
        position = Position.objects.get(id=pk)
        has_permission_or_403(self.request.user, f"organization.can_highlight_positions_{position.bureau.code}")
        position.bureau.highlighted_positions.remove(position)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CapsuleDescriptionView(FieldLimitableSerializerMixin,
                             GenericViewSet,
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


class GradeListView(FieldLimitableSerializerMixin,
                    ReadOnlyModelViewSet):
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


class SkillListView(FieldLimitableSerializerMixin,
                    ReadOnlyModelViewSet):
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


class ClassificationListView(FieldLimitableSerializerMixin,
                             ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given classification.

    list:
    Return a list of all position classifications.
    """

    serializer_class = ClassificationSerializer

    def get_queryset(self):
        queryset = Classification.objects.all()
        queryset = self.serializer_class.prefetch_model(Classification, queryset)
        return queryset
