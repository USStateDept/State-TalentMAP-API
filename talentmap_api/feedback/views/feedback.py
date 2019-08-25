from rest_framework.permissions import IsAuthenticated

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.permissions import isDjangoGroupMember

from talentmap_api.feedback.models import FeedbackEntry
from talentmap_api.feedback.filters import FeedbackEntryFilter
from talentmap_api.feedback.serializers import FeedbackEntrySerializer


class FeedbackUserView(FieldLimitableSerializerMixin,
                       GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.CreateModelMixin):
    """
    Endpoint for creating a new feedback item, open to all authenticated users

    create:
    Creates a feedback entry.

    list:
    Lists all of this user's feedback.
    """

    serializer_class = FeedbackEntrySerializer
    permission_classes = (IsAuthenticated,)
    filter_class = FeedbackEntryFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user.profile)

    def get_queryset(self):
        return get_prefetched_filtered_queryset(FeedbackEntry, self.serializer_class, user=self.request.user.profile)


class FeedbackAdminView(FieldLimitableSerializerMixin,
                        GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin):
    """
    Endpoint for viewing and managing feedback from all users.

    list:
    Lists all feedback.

    destroy:
    Deletes a feedback entry.

    retrieve:
    Retrieves a specific feedback entry.
    """

    serializer_class = FeedbackEntrySerializer
    permission_classes = (isDjangoGroupMember('feedback_editors'),)
    filter_class = FeedbackEntryFilter

    def get_queryset(self):
        return get_prefetched_filtered_queryset(FeedbackEntry, self.serializer_class)
