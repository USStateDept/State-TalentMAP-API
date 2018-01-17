from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.mixins import ActionDependentSerializerMixin

from talentmap_api.bidding.serializers.serializers import WaiverSerializer, WaiverClientSerializer
from talentmap_api.bidding.filters import WaiverFilter
from talentmap_api.bidding.models import Waiver
from talentmap_api.user_profile.models import UserProfile


class WaiverClientView(mixins.ListModelMixin,
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
    Create a new waiver
    '''
    serializer_class = WaiverSerializer

    serializers = {
        "default": WaiverSerializer,
        "partial_update": WaiverClientSerializer,
        "create": WaiverClientSerializer
    }

    filter_class = WaiverFilter
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=UserProfile.objects.get(user=self.request.user))

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).waivers.all()
        queryset = self.serializer_class.prefetch_model(Waiver, queryset)
        return queryset
