from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.bidding.serializers import SurveySerializer
from talentmap_api.bidding.filters import StatusSurveyFilter
from talentmap_api.bidding.models import StatusSurvey
from talentmap_api.user_profile.models import UserProfile


class StatusSurveyView(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.CreateModelMixin,
                       GenericViewSet):
    '''
    list:
    Lists all of the user's status surveys

    retrieve:
    Returns the specified status survey

    partial_update:
    Update the specified status survey

    create:
    Create a new status survey
    '''
    serializer_class = SurveySerializer
    filter_class = StatusSurveyFilter
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=UserProfile.objects.get(user=self.request.user))

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).status_surveys.all()
        queryset = self.serializer_class.prefetch_model(StatusSurvey, queryset)
        return queryset
