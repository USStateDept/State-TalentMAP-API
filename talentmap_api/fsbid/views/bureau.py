import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.schemas import AutoSchema
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
    schema = AutoSchema(
        manual_fields=[
            # Pagination
            coreapi.Field("ordering", location='query', description='Ordering'),
            coreapi.Field("page", location='query', description='Page Index'),
            coreapi.Field("limit", location='query', description='Page Limit'),
            coreapi.Field("getCount", location='query', description='true/false to return total results'),

            coreapi.Field("cps_codes", location='query', description='Handshake status (HS,OP,FP)'),
            coreapi.Field("id", location="query", description="Available Position ids"),
            coreapi.Field("is_available_in_bidcycle", location='query', description='Bid Cycle id'),
            coreapi.Field("is_domestic", location='query', description='Is the position domestic? (true/false)'),
            coreapi.Field("language_codes", location='query', description='Language code'),
            coreapi.Field("position__bureau__code__in", location='query', description='Bureau Code'),
            coreapi.Field("position__grade__code__in", location='query', description='Grade Code'),
            coreapi.Field("position__position_number__in", location='query', description='Position Numbers'),
            coreapi.Field("position__post__code__in", location='query', description='Post id'),
            coreapi.Field("position__post__danger_pay__in", location='query', description='Danger pay'),
            coreapi.Field("position__post__differential_rate__in", location='query', description='Diff. Rate'),
            coreapi.Field("position__post_indicator__in", location='query', description='Use name values from /references/postindicators/'),
            coreapi.Field("position__post__tour_of_duty__code__in", location='query', description='TOD code'),
            coreapi.Field("position__skill__code__in", location='query', description='Skill Code'),
            coreapi.Field("lead_hs_status_code", location='query', description='Handshake code(s) to filter on. (O, R, A, D)'),
            coreapi.Field("position__us_codes__in", location='query', description='Use code values from /references/unaccompaniedstatuses/'),
            coreapi.Field("q", location='query', description='Text search'),
        ]
    )

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
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("ordering", location='query', description='Ordering'),
        ]
    )

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
