import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Max
from django.db.models import Q

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.fsbid.filters import BureauPositionsFilter
from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.available_positions.models import AvailablePositionRankingLock
from talentmap_api.bidding.models import BidHandshake

import talentmap_api.fsbid.services.bureau as services
import talentmap_api.fsbid.services.available_positions as ap_services
import talentmap_api.fsbid.services.employee as empservices
import talentmap_api.fsbid.services.common as com_services
import talentmap_api.fsbid.services.bid as bid_services
import talentmap_api.fsbid.services.classifications as classifications_services

logger = logging.getLogger(__name__)


class FSBidBureauPositionsListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = BureauPositionsFilter

    @swagger_auto_schema(
        manual_parameters=[
            # Pagination
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Index'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Page Limit'),
            openapi.Parameter("getCount", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='true/false to return total results'),

            openapi.Parameter("cps_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake status (HS,OP,FP)'),
            openapi.Parameter("id", openapi.IN_QUERY, type=openapi.TYPE_STRING, description="Available Position ids"),
            openapi.Parameter("is_available_in_bidcycle", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bid Cycle id'),
            openapi.Parameter("is_domestic", openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Is the position domestic? (true/false)'),
            openapi.Parameter("language_codes", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Language code'),
            openapi.Parameter("position__bureau__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Bureau Code'),
            openapi.Parameter("position__grade__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Grade Code'),
            openapi.Parameter("position__position_number__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Position Numbers'),
            openapi.Parameter("position__post__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Post id'),
            openapi.Parameter("position__post__danger_pay__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Danger pay'),
            openapi.Parameter("position__post__differential_rate__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Diff. Rate'),
            openapi.Parameter("position__post_indicator__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use name values from /references/postindicators/'),
            openapi.Parameter("position__post__tour_of_duty__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='TOD code'),
            openapi.Parameter("position__skill__code__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Skill Code'),
            openapi.Parameter("lead_hs_status_code", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Handshake code(s) to filter on. (O, R, A, D)'),
            openapi.Parameter("position__us_codes__in", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Use code values from /references/unaccompaniedstatuses/'),
            openapi.Parameter("htf_ind", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Hard to Fill (Y/N)'),
            openapi.Parameter("q", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Text search'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets all bureau positions
        '''
        hs_query_codes = request.query_params.get('lead_hs_status_code', [])
        # Filter by latest status(update_date) per cp_id
        if len(hs_query_codes) == 0:
            bureau_pos = services.get_bureau_positions(request.query_params, request.META['HTTP_JWT'],
                                                   f"{request.scheme}://{request.get_host()}")
            return Response(services.get_bureau_shortlist_indicator(bureau_pos))

        o_vals = BidHandshake.objects.values('cp_id').annotate(Max('update_date'))
        q_statement = Q()
        for v in o_vals:
            q_statement |= (Q(cp_id__exact=v['cp_id']) & Q(update_date=v['update_date__max']))

        hs_cp_ids = BidHandshake.objects.filter(q_statement).filter(status__in=hs_query_codes).values_list("cp_id", flat=True)

        if len(hs_cp_ids) > 0:
            cp_ids = ','.join(hs_cp_ids)
            query_params_copy = request.query_params.copy()
            query_params_copy["id"] = cp_ids
            query_params_copy._mutable = False
            bureau_pos = services.get_bureau_positions(query_params_copy, request.META['HTTP_JWT'],
                                                       f"{request.scheme}://{request.get_host()}")

            return Response(services.get_bureau_shortlist_indicator(bureau_pos))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})


class FSBidBureauPositionsCSVView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = BureauPositionsFilter

    def get(self, request, *args, **kwargs):
        '''
        Gets all bureau positions for export
        '''
        limit = 9999999
        includeLimit = False
        return services.get_bureau_positions_csv(request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}", limit, includeLimit)


class FSBidBureauPositionView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, pk):
        '''
        Gets a bureau position
        '''
        hasBureauPermissions = empservices.has_bureau_permissions(pk, self.request.META['HTTP_JWT'])
        hasOrgPermissions = empservices.has_org_permissions(pk, self.request.META['HTTP_JWT'])
        result = services.get_bureau_position(pk, request.META['HTTP_JWT'])
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        result['is_locked'] = AvailablePositionRankingLock.objects.filter(cp_id=pk).exists()
        result['has_bureau_permission'] = hasBureauPermissions
        result['has_org_permission'] = hasOrgPermissions

        return Response(result)


class FSBidBureauPositionBidsView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = BureauPositionsFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("ordering", openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering'),
        ])

    def get(self, request, pk):
        '''
        Gets a bureau position's bids
        '''
        result = services.get_bureau_position_bids(pk, request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(result)

class FSBidBureauPositionBidsCSVView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = BureauPositionsFilter

    def get(self, request, pk):
        '''
        Gets a bureau position's bids for export
        '''
        return services.get_bureau_position_bids_csv(self, pk, request.query_params, request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
