from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP

from rest_framework_filters.backends import DjangoFilterBackend

# Common filters for string-type objects
DATETIME_LOOKUPS = ['exact', 'gte', 'gt', 'lte', 'lt', 'range', 'year',
                    'month', 'day', 'hour', 'minute', 'second']
DATE_LOOKUPS = DATETIME_LOOKUPS[:-3]
INTEGER_LOOKUPS = ['exact', 'gte', 'gt', 'lte', 'lt', 'range']
BASIC_TEXT_LOOKUPS = ['exact', 'iexact', 'startswith', 'istartswith',
                      'endswith', 'iendswith']
ALL_TEXT_LOOKUPS = BASIC_TEXT_LOOKUPS + ['contains', 'icontains', 'in', 'isnull']


# This filter backend removes the form rendering which calls the database excessively
class DisabledHTMLFilterBackend(DjangoFilterBackend):

    # This is not covered by tests as it exists solely on the browsable API
    def to_html(self, request, queryset, view):  # pragma: no cover
        return ""


def multi_field_filter(fields, lookup_expr='exact', exclude=False):
    '''
    Curries a function suitable for use as a filter's method.

    Args:
        fields (list) - List of fields to lookup
        lookup_expr (str) - The lookup expression. Defaults to 'exact'
        exclude (bool) - Whether or not to use .exclude instead of .filter - defaults to false.

    Returns:
        callable: A function suitable for use as a filter's method override
    '''

    def filter_method(queryset, name, value):
        q_obj = Q()
        for field in fields:
            lookup = LOOKUP_SEP.join([field, lookup_expr])
            q_obj = q_obj & Q(**{lookup: value})
        if exclude:
            return queryset.exclude(q_obj)
        else:
            return queryset.filter(q_obj)
    return filter_method
