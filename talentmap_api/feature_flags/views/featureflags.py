import datetime
from django.shortcuts import get_object_or_404
# from django.http import Http404

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

from pprint import pprint

class FeatureFlagsView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.CreateModelMixin,
                       GenericViewSet,
                       APIView):

    serializer_class = FeatureFlagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('superuser'))
    # permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('sdkfsjkhf'))

    def get_queryset(self):
        return FeatureFlagsSerializer.objects.last()

    def retrieve(self, request, pk=None, format=None):
        '''
        Gets the Feature Flags file
        '''
        print('-------------------------------------- in views/featureflags.py retrieve --------------------------------------')
        queryset = FeatureFlags.objects.order_by('-date_updated')[0]
        print('---------------------------------------------------------------------------------------------------------------')
        return Response(queryset.feature_flags)


    def perform_create(self, request):
        print('-------------------------------------- in views/featureflags.py perform_create --------------------------------------')
        in_group_or_403(self.request.user, f"superuser")
        # in_group_or_403(self.request.user, f"sdfsdf")
        instance = FeatureFlags()
        logger.info(f"User {self.request.user.id}:{self.request.user} creating feature_flags entry {instance}")
        instance.feature_flags = request.data
        pprint(instance.feature_flags)
        instance.save()
        print('------------------------------------------------------------------------------------------------------------')
        return Response(status=status.HTTP_204_NO_CONTENT)
