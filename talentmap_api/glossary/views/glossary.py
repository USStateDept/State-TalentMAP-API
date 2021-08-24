import csv

from django.http import HttpResponse

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.common_helpers import in_group_or_403
from talentmap_api.fsbid.views.base import BaseView

from talentmap_api.glossary.models import GlossaryEntry
from talentmap_api.glossary.filters import GlossaryEntryFilter
from talentmap_api.glossary.serializers import GlossaryEntrySerializer

import logging
logger = logging.getLogger(__name__)


class GlossaryView(FieldLimitableSerializerMixin,
                   GenericViewSet,
                   mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin):
    """
    retrieve:
    Return the given glossary entry.

    list:
    Return a list of all glossary entries.

    partial_update:
    Update a glossary entry.

    create:
    Creates a glossary entry.
    """

    serializer_class = GlossaryEntrySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_class = GlossaryEntryFilter

    def perform_create(self, serializer):
        in_group_or_403(self.request.user, f"glossary_editors")
        instance = serializer.save(last_editing_user=self.request.user.profile)
        logger.info(f"User {self.request.user.id}:{self.request.user} creating glossary entry {instance}")

    def perform_update(self, serializer):
        in_group_or_403(self.request.user, f"glossary_editors")
        instance = serializer.save(last_editing_user=self.request.user.profile)
        logger.info(f"User {self.request.user.id}:{self.request.user} updating glossary entry {instance}")

    def get_queryset(self):
        return get_prefetched_filtered_queryset(GlossaryEntry, self.serializer_class)


class GlossaryCSVView(BaseView):
    """
    get:
    Download a CSV of the entire glossary
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, serializer):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=TalentMAP-Glossary.csv'

        writer = csv.writer(response)
        writer.writerow(['Title', 'Definition', 'URL'])

        glossary = GlossaryEntry.objects.exclude(is_archived=True).values_list('title', 'definition', 'link')
        for glossary_entry in glossary:
            writer.writerow(glossary_entry)

        return response
