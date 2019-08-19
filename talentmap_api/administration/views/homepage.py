from django.shortcuts import get_object_or_404

from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from talentmap_api.common.permissions import isDjangoGroupMemberOrReadOnly

from talentmap_api.administration.models import HomepageBanner
from talentmap_api.administration.serializers.homepage import HomepageBannerSerializer


class HomepageBannerView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericViewSet, APIView):

    serializer_class = HomepageBannerSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('superuser'))


    def get_queryset(self):
        return HomepageBanner.objects.first()

    def retrieve(self, request, pk=None, format=None):
        '''
        Gets the HomepageBanner
        '''
        queryset = get_object_or_404(HomepageBanner)
        return Response({"text": queryset.text, "is_visible": queryset.is_visible})


    def partial_update(self, request, pk=None, format=None):
        '''
        Updates the HomepageBanner
        '''
        hpb = HomepageBanner.objects.first()
        serializer = self.serializer_class(hpb, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
