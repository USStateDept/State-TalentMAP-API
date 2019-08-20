import datetime

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.permissions import isDjangoGroupMember

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.stats.models import LoginInstance
from talentmap_api.stats.serializers import LoginInstanceSerializer
from talentmap_api.stats.filters import LoginInstanceFilter

import logging
logger = logging.getLogger(__name__)


class UserLoginActionView(GenericViewSet):
    '''
    Tracks login for user
    '''

    permission_classes = (IsAuthenticated,)
    serializer_class = LoginInstanceSerializer

    def submit(self, request, format=None):
        '''
        Logs a user login

        Returns 204 if the action is a success
        '''
        user = UserProfile.objects.get(user=self.request.user)
        login_instance = LoginInstance()

        logger.info(f"User {self.request.user.id}:{self.request.user} is logging in")
        login_instance.user = user
        login_instance.date_of_login = datetime.datetime.now()
        login_instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLoginListView(mixins.ListModelMixin,
                        GenericViewSet):
    '''
    list:
    Lists all logins
    '''
    serializer_class = LoginInstanceSerializer
    filter_class = LoginInstanceFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    def get_queryset(self):
        return get_prefetched_filtered_queryset(LoginInstance, self.serializer_class)


class UserLoginDistinctListView(mixins.ListModelMixin,
                                GenericViewSet):
    '''
    list:
    Lists all logins from distinct user_ids
    '''
    serializer_class = LoginInstanceSerializer
    filter_class = LoginInstanceFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    def get_queryset(self):
        return get_prefetched_filtered_queryset(LoginInstance, self.serializer_class).distinct('user_id').order_by('user_id')
