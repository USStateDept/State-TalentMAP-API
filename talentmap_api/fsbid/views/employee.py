from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import Group

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
        jwt = request.META['HTTP_JWT']
        emp_id = services.get_employee_perdet_seq_num(jwt)

        if emp_id is not None:
            user = request.user.profile
            user.emp_id = str(int(emp_id))
            user.save()

        auth_user = request.user
        # Get the role from the token
        for current_role in services.map_group_to_fsbid_role(jwt):
          auth_user.groups.add(current_role)
          # Remove any roles that the user may have had but have been removed but retain the TM specific roles
          for tm_role in services.ROLE_MAPPING.values():
            if current_role.name != tm_role:
              auth_user.groups.remove(Group.objects.filter(name=tm_role).first())

        auth_user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
