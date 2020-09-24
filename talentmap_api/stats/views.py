import datetime
import logging
import maya
import os

from django.db.models import TextField
from django.db.models.functions import Concat

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.common.common_helpers import in_group_or_403

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.stats.models import LoginInstance, ViewPositionInstance
from talentmap_api.stats.serializers import LoginInstanceSerializer, ViewPositionInstanceSerializer
from talentmap_api.stats.filters import LoginInstanceFilter, ViewPositionInstanceFilter

logger = logging.getLogger(__name__)

class SystemResources(GenericViewSet):
    '''
    System resource utilization
    '''

    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    def get(self, format=None):
        memory = os.popen('free m -m').read() # nosec
        cpu = os.popen('cat /proc/loadavg').read() # nosec
        disk = os.popen('df -h').read() # nosec
        return Response(data={"memory":memory, "cpu":cpu, "disk":disk})


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
        login_instance.details = request.data.get('details', {})
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


class ViewPositionActionView(GenericViewSet):
    '''
    Tracks position view
    '''

    permission_classes = (IsAuthenticated,)
    serializer_class = ViewPositionInstanceSerializer

    def submit(self, request, format=None):
        '''
        Logs a position view

        Returns 204 if the action is a success
        '''
        user = UserProfile.objects.get(user=self.request.user)
        view_instance = ViewPositionInstance()

        view_instance.user = user
        view_instance.date_of_view = datetime.datetime.now()
        view_instance.date_of_view_day = maya.now().datetime().strftime('%m/%d/%Y')
        view_instance.date_of_view_week = maya.now().datetime().strftime('%V/%Y')
        view_instance.position_id = request.data.get('position_id')
        view_instance.position_type = request.data.get('position_type', 'AP')

        POSITION_TYPE_CHOICES = ['AP', 'PV', 'FP']

        if (view_instance.position_type in POSITION_TYPE_CHOICES) is False:
            return Response(data=f"Invalid position_type value of {view_instance.position_type}. Choose from {POSITION_TYPE_CHOICES}", status=status.HTTP_400_BAD_REQUEST)
        else:
            view_instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class ViewPositionListView(mixins.ListModelMixin,
                           GenericViewSet):
    '''
    list:
    Lists all position views
    '''
    serializer_class = ViewPositionInstanceSerializer
    filter_class = ViewPositionInstanceFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    def get_queryset(self):
        return get_prefetched_filtered_queryset(ViewPositionInstance, self.serializer_class)


class ViewPositionDistinctListView(mixins.ListModelMixin,
                                   GenericViewSet):
    '''
    list:
    Lists all position views from distinct, concatenated user_id + position_id + position_type, deduplicated within each week
    '''
    serializer_class = ViewPositionInstanceSerializer
    filter_class = ViewPositionInstanceFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    def get_queryset(self):
        return get_prefetched_filtered_queryset(ViewPositionInstance, self.serializer_class).annotate(distinct_name=Concat('position_type', 'position_id', 'user_id', 'date_of_view_week', output_field=TextField())).order_by('distinct_name').distinct('distinct_name')
