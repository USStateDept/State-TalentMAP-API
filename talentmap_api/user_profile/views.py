from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

from talentmap_api.common.mixins import ActionDependentSerializerMixin

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.serializers import UserProfileSerializer, UserProfileWritableSerializer

from talentmap_api.position.models import Position
from talentmap_api.position.serializers import PositionSerializer


class UserProfileView(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      ActionDependentSerializerMixin,
                      GenericViewSet):
    """
    retrieve:
    Return the current user profile
    """
    serializers = {
        "default": UserProfileSerializer,
        "partial_update": UserProfileWritableSerializer
    }

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        queryset = UserProfile.objects.filter(user=self.request.user)
        self.serializer_class.prefetch_model(UserProfile, queryset)
        return queryset.first()
