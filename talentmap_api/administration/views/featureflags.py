from django.shortcuts import get_object_or_404

from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.permissions import isDjangoGroupMemberOrReadOnly

from talentmap_api.administration.models import FeatureFlags
from talentmap_api.administration.serializers.featureflags import FeatureFlagsSerializer

class FeatureFlagsView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet, APIView):

    serializer_class = FeatureFlagsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('superuser'))


    def get_queryset(self):
        return FeatureFlagsSerializer.objects.first()

    def retrieve(self, request, pk=None, format=None):
        '''
        Gets the Feature Flags file
        '''
        print('-------------------------------------- in feature flags --------------------------------------')
        print('FeatureFlags', FeatureFlags)
        queryset = get_object_or_404(FeatureFlags)
        print('queryset:', queryset)
        print('queryset.content:', queryset.content)
        return Response({"content": queryset.content})

    def partial_update(self, request, pk=None, format=None):
        '''
        Updates the Feature Flags file
        '''
        print('-------------------------------------- updating feature flags --------------------------------------')
        print('-------------------------------------- request.data:', request.data)
        hpb = FeatureFlags.objects.first()
        print('hpb:', hpb)
        serializer = self.serializer_class(hpb, data=request.data, partial=True)
        print('serializer:', serializer)
        if serializer.is_valid():
            print('serializer.errors:', serializer.errors)
            serializer.save()
            print('-------------------------------------- serializer valid :)')
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            print('serializer.errors:', serializer.errors)
            print('-------------------------------------- serializer NOT valid :(')
            return Response(status=status.HTTP_400_BAD_REQUEST)

