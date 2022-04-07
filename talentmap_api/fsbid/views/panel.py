import logging
import coreapi

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Max
from django.db.models import Q

from rest_framework.response import Response
from rest_framework import status

from rest_condition import Or
from talentmap_api.common.permissions import isDjangoGroupMember


from talentmap_api.fsbid.views.base import BaseView

import talentmap_api.fsbid.services.panel as services

logger = logging.getLogger(__name__)

class PanelDatesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel dates
        '''
        return Response(services.get_panel_dates(request.query_params, request.META['HTTP_JWT']))

class PanelCategoriesView(BaseView):
    permission_classes = [Or(isDjangoGroupMember('cdo'), isDjangoGroupMember('ao_user'))]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter("page", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter("limit", openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
        ])

    def get(self, request, *args, **kwargs):
        '''
        Gets panel categories
        '''
        return Response(services.get_panel_categories(request.query_params, request.META['HTTP_JWT']))
