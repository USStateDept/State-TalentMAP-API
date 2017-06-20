from rest_framework_filters.backends import DjangoFilterBackend

# Common filters for string-type objects
DATETIME_LOOKUPS = ['exact', 'gte', 'gt', 'lte', 'lt', 'range', 'year',
                    'month', 'day', 'hour', 'minute', 'second']
DATE_LOOKUPS = DATETIME_LOOKUPS[:-3]
INTEGER_LOOKUPS = ['exact', 'gte', 'gt', 'lte', 'lt', 'range']
BASIC_TEXT_LOOKUPS = ['exact', 'iexact', 'startswith', 'istartswith',
                      'endswith', 'iendswith']
ALL_TEXT_LOOKUPS = BASIC_TEXT_LOOKUPS + ['contains', 'icontains', 'in']


# This filter backend removes the form rendering which calls the database excessively
class DisabledHTMLFilterBackend(DjangoFilterBackend):

    # This is not covered by tests as it exists solely on the browsable API
    def to_html(self, request, queryset, view):  # pragma: no cover
        return ""
