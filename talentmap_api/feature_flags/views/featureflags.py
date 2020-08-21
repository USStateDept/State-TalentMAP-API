import datetime
from django.shortcuts import get_object_or_404

from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.permissions import isDjangoGroupMemberOrReadOnly
from talentmap_api.common.common_helpers import in_group_or_403


from talentmap_api.feature_flags.models import FeatureFlags
from talentmap_api.feature_flags.serializers.featureflags import FeatureFlagsSerializer

import logging
logger = logging.getLogger(__name__)


class FeatureFlagsView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.CreateModelMixin,
                       GenericViewSet,
                       APIView):

    serializer_class = FeatureFlagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('superuser'))

    def get_queryset(self):
        return FeatureFlagsSerializer.objects.last()

    def retrieve(self, request, pk=None, format=None):
        '''
        Gets the Feature Flags file
        '''
        queryset = FeatureFlags.objects.order_by('-date_updated')
        if not queryset:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(queryset[0].feature_flags)


    def perform_create(self, request):
        in_group_or_403(self.request.user, f"superuser")
        instance = FeatureFlags()
        logger.info(f"User {self.request.user.id}:{self.request.user} creating feature_flags entry {instance}")
        instance.feature_flags = request.data
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
