import logging

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from talentmap_api.common.permissions import isDjangoGroupMemberOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth.models import Group

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.employee as services

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
            user.emp_id = str(emp_id)
            user.save()

        auth_user = request.user

        # Get the valid and mapped roles from the token
        user_roles = services.map_group_to_fsbid_role(jwt)

        # Add roles
        for current_role in user_roles:
            auth_user.groups.add(current_role)

        # Remove any roles that the user has lost since the last time they logged in
        for role in services.ROLE_MAPPING.values():
            if role not in user_roles.values_list('name', flat=True):
                auth_user.groups.remove(Group.objects.filter(name=role).first())

        auth_user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)


class FSBidBureauUserPermissionsView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('bureau_user'))
    '''
    Get an employee's assigned bureaus
    '''
    def get(self, request):
        result = services.get_bureau_permissions(request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)


class FSBidOrgUserPermissionsView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly, isDjangoGroupMemberOrReadOnly('post_user'))
    '''
    Get an employee's assigned organizations
    '''
    def get(self, request):
        result = services.get_org_permissions(request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        if result is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(result)
