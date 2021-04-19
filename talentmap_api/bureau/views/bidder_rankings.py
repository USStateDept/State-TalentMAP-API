import logging
import coreapi
import time

from rest_condition import Or

from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from rest_framework.response import Response

import talentmap_api.bureau.services.rankings as bureau_services

from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


class BureauBiddersRankings(APIView):

    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('bureau_user')), ]

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("perdet", location='query', description='perdet of Bureau bidder'),
        ]
    )

    def get(self, request, pk):
        """
        Return position information for all of bidders' bids including their ranking information for those positions
        """
        return Response(bureau_services.get_bidder_bids_and_rankings(self, request, pk))

