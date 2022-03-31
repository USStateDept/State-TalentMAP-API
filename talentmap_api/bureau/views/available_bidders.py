import logging
import coreapi
from rest_condition import Or

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.views import APIView
from rest_framework.response import Response

import talentmap_api.bureau.services.available_bidders as services
import talentmap_api.fsbid.services.client as client_services
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


class AvailableBiddersListView(APIView):

    permission_classes = [Or(isDjangoGroupMember('post_user'), isDjangoGroupMember('bureau_user')), ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Which field to use when ordering the results.')
        ])

    def get(self, request):
        """
        Return users in Available Bidders list for Bureau
        """
        return Response(client_services.get_available_bidders(request.META['HTTP_JWT'], False, request.query_params, f"{request.scheme}://{request.get_host()}"))


class AvailableBiddersCSVView(APIView):
    permission_classes = [Or(isDjangoGroupMember('post_user'), isDjangoGroupMember('bureau_user')), ]

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the users in Available Bidders for CSV export for Bureau
        """
        return services.get_available_bidders_csv(request)