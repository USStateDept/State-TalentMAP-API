import pydash
import json
import maya
import logging

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
from talentmap_api.bidding.models import BidHandshakeCycle
from talentmap_api.messaging.filters import NotificationFilter
from talentmap_api.messaging.serializers import NotificationSerializer

logger = logging.getLogger(__name__)


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
            'owner': self.request.user.profile,
        }

        exclude_params = {
            'id__in': []
        }

        matches = Notification.objects.filter(owner=self.request.user.profile).values()

        # This is inefficient, but we have to fetch all notifications to find out which ones have the requested tags.
        if tags:
            matchesClone = pydash.filter_(matches, lambda x: set(tags).issubset(set(x['tags'] or [])))
            matchesClone = pydash.map_(matchesClone, 'id')
            # Only append to params if tags exists, so that we don't inadvertently pass an empty array
            params['id__in'] = matchesClone
        

        # Don't show notifications for handshakes that are in an unrevealed bid cycle
        for x in matches:
            try:
                meta = pydash.get(x, 'meta') or '{}'
                meta = json.loads(meta)
                bidcycle_id = pydash.get(meta, 'bidcycle_id')
                cycles = BidHandshakeCycle.objects.filter(cycle_id=bidcycle_id)
                if cycles.first():
                    cycle = cycles.first()
                    allowed_date = cycle.handshake_allowed_date
                    if allowed_date:
                        if allowed_date > maya.now().datetime():
                            exclude_params['id__in'].append(pydash.get(x, 'id'))
            except Exception as e:
                logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")
        

        queryset = Notification.objects.filter(**params).exclude(**exclude_params)
        self.serializer_class.prefetch_model(Notification, queryset)
        return queryset
