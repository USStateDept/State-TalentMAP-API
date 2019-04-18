from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin

from talentmap_api.bidding.serializers.serializers import SurveySerializer, BidSerializer, WaiverSerializer
from talentmap_api.bidding.serializers.prepanel import PrePanelSerializer
from talentmap_api.bidding.filters import StatusSurveyFilter, BidFilter, WaiverFilter
from talentmap_api.bidding.models import StatusSurvey, Bid, Waiver
from talentmap_api.position.serializers import AssignmentSerializer
from talentmap_api.position.filters import AssignmentFilter

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.filters import ClientFilter
from talentmap_api.user_profile.serializers import ClientSerializer, ClientDetailSerializer


class CdoClientView(ActionDependentSerializerMixin,
                    FieldLimitableSerializerMixin,
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

    serializers = {
        "default": ClientSerializer,
        "retrieve": ClientDetailSerializer,
    }

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
            "bidding_no_handshake": profile.direct_reports.exclude(bidlist=None).filter(bidlist__handshake_offered_date=None).distinct().count(),
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


class CdoClientAssignmentView(FieldLimitableSerializerMixin, mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Lists all of the specified client's assignments
    """

    serializer_class = AssignmentSerializer
    permission_classes = (IsAuthenticated,)
    filter_class = AssignmentFilter

    def get_queryset(self):
        client = get_object_or_404(UserProfile.objects.filter(cdo=self.request.user.profile), id=self.request.parser_context.get("kwargs").get("pk"))
        queryset = client.assignments.all()
        self.serializer_class.prefetch_model(StatusSurvey, queryset)
        return queryset


class CdoClientBidView(FieldLimitableSerializerMixin,
                       ActionDependentSerializerMixin,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    """
    list:
    Lists all of the specified client's bids

    retrieve:
    Retrieves a specific bid, with pre-panel screening
    """

    serializer_class = BidSerializer

    serializers = {
        "default": BidSerializer,
        "retrieve": PrePanelSerializer,
    }

    filter_class = BidFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        client = get_object_or_404(UserProfile.objects.filter(cdo=self.request.user.profile), id=self.request.parser_context.get("kwargs").get("pk"))
        queryset = client.bidlist.all()
        self.serializer_class.prefetch_model(Bid, queryset)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        return get_object_or_404(queryset, id=self.request.parser_context.get("kwargs").get("bid_id"))


class CdoClientWaiverView(FieldLimitableSerializerMixin, mixins.ListModelMixin, GenericViewSet):
    """
    list:
    Lists all of the specified client's waivers
    """

    serializer_class = WaiverSerializer
    filter_class = WaiverFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        client = get_object_or_404(UserProfile.objects.filter(cdo=self.request.user.profile), id=self.request.parser_context.get("kwargs").get("pk"))
        queryset = client.waivers.all()
        self.serializer_class.prefetch_model(Waiver, queryset)
        return queryset
