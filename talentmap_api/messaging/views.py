from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.apps import apps

from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification
from talentmap_api.messaging.filters import NotificationFilter
from talentmap_api.messaging.serializers import NotificationSerializer


class NotificationView(FieldLimitableSerializerMixin,
                       GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    '''
    partial_update:
    Edits a saved notification

    retrieve:
    Retrieves a specific notification

    list:
    Lists all notifications

    destroy:
    Deletes a specified notification
    '''

    serializer_class = NotificationSerializer
    filter_class = NotificationFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Notification.objects.filter(owner=self.request.user.profile)
        self.serializer_class.prefetch_model(Notification, queryset)
        return queryset
