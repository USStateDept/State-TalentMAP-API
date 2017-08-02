from django.core.urlresolvers import resolve
from django.utils.six.moves.urllib.parse import urlparse

from django.core.exceptions import FieldError
from django.core.exceptions import ValidationError

from django.db.models import Q


def resolve_path_to_view(request_path):
    '''
    Returns a viewset if the path resolves to a view
    '''
    # Resolve the path to a view
    view, args, kwargs = resolve(urlparse(request_path)[2])

    # Instantiate the view
    view = view.cls()

    return view


def validate_filters_exist(filter_list, filter_class):
    for filter in filter_list.keys():
        # If our filter is in the declared_filter list, it is a valid filter (these have some manual parsing)
        if filter not in filter_class.declared_filters:
            # If the filter is NOT a declared filter, it is automatic from the model and we
            # can verify that the data within is valid by performing a basic filtering
            try:
                value = filter_list[filter]
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                filter_class.Meta.model.objects.filter(Q(**{f"{filter}": value}))
            except FieldError:
                # Filter is using a bad field, return False
                # We do NOT check for bad values (i.e. saving a search for a missing ID)
                # because we need to allow PATCHing bad searches in that case
                raise ValidationError(f"Filter {filter} is not valid on this endpoint")
