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

from pprint import pprint
class FeatureFlagsView(mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.CreateModelMixin,
                       GenericViewSet,
                       APIView):

    serializer_class = FeatureFlagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('superuser'))


    def get_queryset(self):
        return FeatureFlagsSerializer.objects.all()

    def retrieve(self, request, pk=None, format=None):
        '''
        Gets the Feature Flags file
        '''
        print('-------------------------------------- in views/featureflags.py retrieve --------------------------------------')
        queryset = get_object_or_404(FeatureFlags)
        print('FeatureFlags model:', FeatureFlags)
        print('queryset:', queryset)
        l = dir(queryset)
        pprint(l)
        pprint(queryset.feature_flags)
        print('------------------------------------------------------------------------------------------------------------')
        return Response(queryset.feature_flags)


    def perform_create(self, serializer):
        print('-------------------------------------- in views/featureflags.py perform_create --------------------------------------')
        print('serializer:', serializer)
        pprint('serializer.is_valid():', serializer.is_valid())
        print('------------------------------------------------------------------------------------------------------------')

        in_group_or_403(self.request.user, f"superuser")
        instance = serializer.save(last_editing_user=self.request.user.profile)
        logger.info(f"User {self.request.user.id}:{self.request.user} creating feature_flags entry {instance}")

