from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django.contrib.postgres.search import SearchVector
from django.core.exceptions import FieldDoesNotExist

from rest_framework_filters.backends import DjangoFilterBackend
from rest_framework import filters as restFilters
import rest_framework_filters as drff_filters

# Common filters for string-type objects
DATETIME_LOOKUPS = ['exact', 'gte', 'gt', 'lte', 'lt', 'range', 'year',
                    'month', 'day', 'hour', 'minute', 'second']
DATE_LOOKUPS = DATETIME_LOOKUPS[:-3]
INTEGER_LOOKUPS = ['exact', 'gte', 'gt', 'lte', 'lt', 'range', 'in']
BASIC_TEXT_LOOKUPS = ['exact', 'iexact', 'startswith', 'istartswith',
                      'endswith', 'iendswith']
ALL_TEXT_LOOKUPS = BASIC_TEXT_LOOKUPS + ['contains', 'icontains', 'in', 'isnull']
FOREIGN_KEY_LOOKUPS = ['exact', 'in', 'isnull']
ARRAY_LOOKUPS = ['contains', 'contained_by', 'len', 'overlap']


# This filter backend removes the form rendering which calls the database excessively
class DisabledHTMLFilterBackend(DjangoFilterBackend):

    # This is not covered by tests as it exists solely on the browsable API
    def to_html(self, request, queryset, view):  # pragma: no cover
        return ""


class RelatedOrderingFilter(restFilters.OrderingFilter):
    """
    Django rest framework does not natively support ordering by a nested object's
    data, to allow this, we override "is_valid_field" to verify that the ordering
    parameter is a valid nested field

    DRF issue https://github.com/tomchristie/django-rest-framework/issues/1005
    """

    related_field_types = ["OneToOneField", "ManyToManyField", "ForeignKey"]

    def is_valid_field(self, model, field):
        # Split with maximum splits of 1, so if passed xx__yy__zz, we get [xx, yy__zz]
        components = field.split(LOOKUP_SEP, 1)
        try:
            field = model._meta.get_field(components[0])

            if field.get_internal_type() in self.related_field_types and len(components) > 1:
                return self.is_valid_field(field.related_model, components[1])

            return True
        except FieldDoesNotExist:
            return False

    def remove_invalid_fields(self, queryset, fields, ordering, view):
        return [term for term in fields
                if self.is_valid_field(queryset.model, term.lstrip('-'))]


class NumberInFilter(drff_filters.BaseInFilter, drff_filters.NumberFilter):
    '''
    Combines the in and number filter to support M2M in filtering
    '''
    pass


def negate_boolean_filter(lookup_expr):
    '''
    Curries a function which executes a boolean filter, but negating the incoming value.
    This is needed because in the case of reversing a many to many relationship
    an exclusion is not always equivalent to a negative filter.

    For example:
    TourOfDuty.objects.filter(posts__positions__isnull=False) will return different results from
    TourOfDuty.objects.exclude(posts__positions__isnull=True)
    '''
    def filter_method(queryset, name, value):
        value = not value
        lookup = LOOKUP_SEP.join([name, lookup_expr])
        return queryset.filter(Q(**{lookup: value})).distinct()

    return filter_method


def multi_field_filter(fields, lookup_expr='exact', exclude=False):
    '''
    Curries a function suitable for use as a filter's method. This function allows
    for filtering across multiple relationships, for example, a filter parameter of
    'available' might wish to be valid only if 'fieldA' and 'fieldB' are both valid.
    This is achieved by calling multi_field_filter(['fieldA', 'fieldB']) and using
    the returned method as the 'method' parameter of the filter.

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
        return filter_or_exclude_queryset(queryset, q_obj, exclude)
    return filter_method


def full_text_search(fields):
    '''
    Curries a function suitable for use as a filter's method to perform FTS.
    (This function should be expanded as FTS functionality needs additional complexity)

    Args:
        fields (list) - List of fields for search vectors which will be combined for the search

    Returns:
        callable: A function suitable for use as a filter's method override
    '''
    # Create our vectors
    vectors = [SearchVector(x) for x in fields]
    final_vector = vectors[0]

    # Each column creates its own search vector, but since we're using the same
    # term across all vectors, we need to combine them. This is done via addition operator
    for vector in vectors[1:]:
        final_vector += vector

    def filter_method(queryset, name, value):
        # Create our q dict for the contains operation - FTS prefix matching is finnicky via django
        # may want to consider hopping over to something like django-haystack to clean this up in the future
        q_obj = Q(**{"search": value})
        for q in [Q(**{f"{x}__icontains": value}) for x in fields]:
            q_obj = q_obj | q

        # We need to ensure we only get distinct items - since FTS spans multiple columns this could cause duplication
        # To accomplish this we grab the id's of matching FTS search and return a queryset filtered to those IDs
        # We don't use .distinct() here because it is not respected if filtered afterwards, and, distinct will
        # sort the queryset which is un-needed at this stage of filtering.

        # Use queryset.all() to acquire a duplicate of the queryset
        id_list = queryset.all().annotate(search=final_vector).filter(q_obj).values_list('id', flat=True)
        return queryset.filter(id__in=id_list)
    return filter_method


def array_field_filter(lookup_expr, exclude=False):
    '''
    Curries a function suitable for use as a filter's method to support Postgres ArrayFields.

    Args:
        lookup_expr - The lookup expression this method should support
        exclude - Whether this lookup should include or exclude the values

    Returns:
        callable: A function suitable for use as a filter's method override
    '''

    def filter_method(queryset, name, value):
        lookup = LOOKUP_SEP.join([name, lookup_expr])
        q_obj = Q(**{lookup: value.split(',')})
        return filter_or_exclude_queryset(queryset, q_obj, exclude)

    return filter_method


def filter_or_exclude_queryset(queryset, filters, exclude=False):
    '''
    Filters or excludes a queryset based upon specified q_obj filters
    '''
    if exclude:
        return queryset.exclude(filters)
    else:
        return queryset.filter(filters)
