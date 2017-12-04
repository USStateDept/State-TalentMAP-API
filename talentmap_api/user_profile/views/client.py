from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.bidding.serializers import SurveySerializer
from talentmap_api.bidding.filters import StatusSurveyFilter
from talentmap_api.bidding.models import StatusSurvey, Bid

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.filters import ClientFilter
from talentmap_api.user_profile.serializers import ClientSerializer


class CdoClientView(FieldLimitableSerializerMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):

    """
    list:
    Lists all of the user's clients' profiles

    retrieve:
    Returns a specific client's profile
    """

    serializer_class = ClientSerializer
    filter_class = ClientFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return get_prefetched_filtered_queryset(UserProfile, self.serializer_class, cdo=self.request.user.profile)


class CdoClientStatisticsView(APIView):
    '''
    Returns statistics about a CDO's client portfolio
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None, **url_arguments):
        '''
        Returns an array of statistics
        '''
        profile = get_object_or_404(UserProfile, user=request.user)

        statistics = {
            "all_clients": profile.direct_reports.count(),
            "bidding_clients": profile.direct_reports.exclude(bidlist=None).count(),
            "in_panel_clients": profile.direct_reports.filter(bidlist__status=Bid.Status.in_panel).count(),
            "on_post_clients": profile.direct_reports.exclude(assignments__current_for_position=None).count()
        }

        return Response(statistics, status=status.HTTP_200_OK)


class CdoClientSurveyView(FieldLimitableSerializerMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):

    """
    list:
    Lists all of the specified client's status surveys
    """

    serializer_class = SurveySerializer
    filter_class = StatusSurveyFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        client = get_object_or_404(UserProfile.objects.filter(cdo=self.request.user.profile), id=self.request.parser_context.get("kwargs").get("pk"))
        queryset = client.status_surveys.all()
        self.serializer_class.prefetch_model(StatusSurvey, queryset)
        return queryset
