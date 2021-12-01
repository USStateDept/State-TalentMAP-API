import coreapi

from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.permissions import IsAuthenticated

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.classifications as classifications_services


class FSBidClassificationsView(BaseView):

    permission_classes = (IsAuthenticated,)

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("perdet_seq_num", location='query', description='ID of user'),
        ]
    )

    def get(self, request, pk):
        '''
        Get user's classifications
        '''
        return Response(classifications_services.get_client_classification(request.META['HTTP_JWT'], pk))
