import rest_framework_filters as filters
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.filters import UserProfileFilter

from talentmap_api.common.serializers import StaticRepresentationField
from talentmap_api.common.filters import INTEGER_LOOKUPS, ALL_TEXT_LOOKUPS, DATE_LOOKUPS, FOREIGN_KEY_LOOKUPS
from talentmap_api.common.mixins import FieldLimitableSerializerMixin


def generate_historical_view(model_class, serializer, filter):
    '''
    Generate a view and filter to support historical records for the specified model class
    '''

    class HistoricalFilter(filter):
        history_user = filters.RelatedFilter(UserProfileFilter, name='history_user', queryset=UserProfile.objects.all())

        class Meta(filter.Meta):
            model = model_class.history.model
            fields = {
                **filter.Meta.fields,
                "id": INTEGER_LOOKUPS,
                "history_date": DATE_LOOKUPS,
                "history_change_reason": ALL_TEXT_LOOKUPS,
                "history_type": ALL_TEXT_LOOKUPS,
                "history_user": FOREIGN_KEY_LOOKUPS
            }

    class HistoricalSerializer(serializer):
        history_user = StaticRepresentationField(read_only=True)

        class Meta(serializer.Meta):
            model = model_class.history.model
            fields = "__all__"
            nested = {}  # No nesting serializers here - the FK traversal doesn't cascade (yet)

    class HistoricalView(FieldLimitableSerializerMixin,
                         ReadOnlyModelViewSet):
        """
        retrieve:
        Return a specific historical entry.

        list:
        Return a list of all historical entries.
        """

        serializer_class = HistoricalSerializer
        filter_class = HistoricalFilter
        lookup_field = "history_id"
        lookup_value_regex = "[0-9]+"

        def get_queryset(self):
            instance = get_object_or_404(model_class, pk=self.request.parser_context.get("kwargs").get("instance_id"))
            return self.serializer_class.prefetch_model(model_class, instance.history)

    return HistoricalView
