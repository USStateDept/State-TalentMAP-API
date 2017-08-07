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
        '''
        The filter class (a subclass of FilterSet) passed into this function has knowledge of all
        implicit and declared filters. Declared filters are those explicity instantiated (typically
        in a file like filters.py), and typically are method filters or related filter sets.

        We can only validate in this method filters which are implicit (and therefore a true model level filter)
        as the declared filters perform their validation on-call, and may or may not actually filter at
        the object level; invalid values for declared filters either return a 400 when queried or have no effect.

        This method does not check if the supplied value for the filter is valid, as we need to allow users to
        PATCH old or outdated saved searches, it simply evaluates if the filters are supported on the model for
        that filter class.

        Args:
            - filter_list (dict) - A dictionary containing filters and values representing a saved search
            - filter_class (FilterSet) - The FilterSet subclass which will evaluate the filter list
        '''
        # Perform validation if our filter is not in the set of declared (non-implicit) filters
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
