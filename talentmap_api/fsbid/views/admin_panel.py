import logging

from rest_framework.response import Response
from rest_framework import status

import talentmap_api.fsbid.services.admin_panel as services
from talentmap_api.fsbid.views.base import BaseView


logger = logging.getLogger(__name__)


class CreateRemarkView(BaseView):

    def post(self, request):
        '''
        Saves a new Remark
        '''
        try:
            services.submit_create_remark(request.data, request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}. User {self.request.user}")
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY)
