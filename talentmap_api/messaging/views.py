import pydash

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
        # Oracle and Django don't play nice with JSON. This makes filtering by an array of tags difficult.
        # We comma separate the tags provided in the ?tags query parameter (ex: ?tags=a,b,c).
        tags = [x for x in self.request.GET.get('tags', '').split(',')]
        # filter out an empty strings
        tags = pydash.without(tags, '')

        matches = []

        params = {
            'owner': self.request.user.profile
        }

        # This is inefficient, but we have to fetch all notifications to find out which ones have the requested tags.
        if tags:
            matches = Notification.objects.filter(owner=self.request.user.profile).values()
            matches = pydash.filter_(matches, lambda x: set(tags).issubset(set(x['tags'] or [])))
            matches = pydash.map_(matches, 'id')
            # Only append to params if tags exists, so that we don't inadvertently pass an empty array
            params['id__in'] = matches

        queryset = Notification.objects.filter(**params)
        self.serializer_class.prefetch_model(Notification, queryset)
        return queryset
