from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework import mixins
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.messaging.models import Notification
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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Notification.objects.filter(owner=self.request.user.profile)
        self.serializer_class.prefetch_model(Notification, queryset)
        return queryset
