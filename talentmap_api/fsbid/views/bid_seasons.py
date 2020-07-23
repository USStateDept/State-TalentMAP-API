import logging

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.response import Response

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.bid_season as services

logger = logging.getLogger(__name__)


class FSBidBidSeasonsListView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        '''
        Gets all bid seasons
        '''
        return Response(services.get_bid_seasons(request.query_params.get('bsn_future_vacancy_ind', None), request.META['HTTP_JWT']))
