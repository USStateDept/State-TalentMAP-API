import coreapi

from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.classifications as classifications_services


class FSBidClassificationsView(BaseView):

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("id", openapi.IN_PATH, type=openapi.TYPE_STRING, description='perdet of user')
        ])

    def get(self, request, pk):
        '''
        Get user's classifications
        '''
        return Response(classifications_services.get_client_classification(request.META['HTTP_JWT'], pk))
