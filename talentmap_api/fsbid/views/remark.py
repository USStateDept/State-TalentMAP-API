import logging
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_condition import Or

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.remark as services
from talentmap_api.common.permissions import isDjangoGroupMember

logger = logging.getLogger(__name__)


class RemarkView(BaseView):
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'rmrkseqnum': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Seq Num'),
            'rmrkrccode': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Category Code'),
            'rmrkordernum': openapi.Schema(type=openapi.TYPE_INTEGER, description='Remark Order Num'),
            'shortDescription': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Short Description'),
            'rmrkmutuallyexclusiveind': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Mutually Exclusive Indicator'),
            'longDescription': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Text'),
            'activeIndicator': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Active Indicator'),
            'rmrkcreateid': openapi.Schema(type=openapi.TYPE_INTEGER, description='Remark Creator ID'),
            'rmrkupdateid': openapi.Schema(type=openapi.TYPE_INTEGER, description='Remark Updater ID'),
            'rmrkupdatedate': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Updated Date'),
        }
    ))

    def put(self, request):
        '''
        Edit remark to mark inactive/active
        '''
        return Response(services.edit_remark(request.data, request.META['HTTP_JWT']))


class RemarkActionView(BaseView):
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'rmrkCategory': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Category Code'),
            'shortDescription': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Short Description'),
            'longDescription': openapi.Schema(type=openapi.TYPE_STRING, description='Remark Text'),
            'rmrkInsertionList': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(
                type=openapi.TYPE_STRING,
            ), description='Insertion List'),
        }
    ))

    def post(self, request):
        '''
        Create remark
        '''
        try:
            services.create_remark_and_remark_insert(request.data, request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.info(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)

