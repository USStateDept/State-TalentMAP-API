from django.contrib.auth.models import Permission
from django.core.urlresolvers import resolve
from django.http import QueryDict
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.datastructures import MultiValueDict

from django.core.exceptions import FieldError, ValidationError, PermissionDenied

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


def get_filtered_queryset(filter_class, filters):
    '''
    This function accepts a filter class (some implementation of FilterSet)
    and dict of supported filters, and returns the queryset after filtering

    Args:
        - filter_class (class) - The filterset class
        - filters (dict) - Dictionary of valid filters for this view

    Returns
        - QuerySet (object) - The filtered queryset
    '''

    '''
    The goal of this function is to provide the queryset as it exists on an
    endpoint's view, after filtering has been completed. Naively, we might
    attempt using a Q object and the filters dict to filter the queryset. This
    would work for most cases, with the exception of declared filters such as
    'q' or 'is_available'; any custom filters such as these would not be processable
    and in fact would throw an error.

    The solution to this, is to use the view's filter class. Essentially, we trick
    the filter class into thinking we have passed a valid request. The steps to
    accomplish this are the following:
        1. Turn the filters into a MultiValueDict - this is required later for
           the construction of our QueryDict, to prevent nested lists
        2. Create a QueryDict of the filters - we need this to support some function
           calls that are made internally which would error out on a normal dict
        3. Create a fake request object, and set the QueryDict as the query_params
        4. Get the subset filter class
        5. Instantiate the subset filter class using query_params and the faked request
        6. Get the queryset from the filter class
    '''
    new_filters = MultiValueDict()

    for key, value in filters.items():
        if isinstance(value, list):
            new_filters.setlist(key, value)
        else:
            new_filters.appendlist(key, value)

    query_params = QueryDict('', mutable=True)
    query_params.update(new_filters)

    # Your daily dose of python wizardry: https://docs.python.org/3/library/functions.html#type
    fake_request = type('obj', (object,), {'query_params': query_params})

    queryset = filter_class.get_subset(query_params)(data=query_params, request=fake_request).qs

    return queryset


def get_permission_by_name(name):
    '''
    Gets the permission object associated with the specified name, in app_label.codename format

    Args:
        - name (String) - The permission name, in app_label.codename format

    Returns
        - Permission (object) - The permission
    '''

    app_label, codename = name.split(".", 1)
    try:
        return Permission.objects.get(content_type__app_label=app_label,
                                      codename=codename)
    except Permission.DoesNotExist:
        raise Exception(f"Permission {app_label}.{codename} not found.")


def has_permission_or_403(user, permission):
    '''
    This function mimics the functionality of get_object_or_404, but for permissions.
    Pass the string permission codename as 'permission', and the function will do nothing
    if the user has that permission, or raise a PermissionDenied exception if the user lacks the permission.

    Args:
        - user (Object) - The user instance
        - permission (String) - The permission codename string
    '''

    if not user.has_perm(permission):
        raise PermissionDenied
