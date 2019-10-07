from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.employee as services

import logging
logger = logging.getLogger(__name__)


class FSBidEmployeePerdetSeqNumActionView(BaseView):

    permission_classes = (IsAuthenticated,)

    def put(self, request, *args, **kwargs):
        '''
        Sets the employee perdet_seq_num (emp_id) for the user
        '''
        emp_id = services.get_employee_perdet_seq_num(request.META['HTTP_JWT'])
        if emp_id is None:
          return Response(status=status.HTTP_404_NOT_FOUND)

        user = request.user.profile
        user.emp_id = emp_id
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
