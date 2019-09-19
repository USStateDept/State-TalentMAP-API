import datetime
import logging

from pydoc import locate

from dateutil.relativedelta import relativedelta
from dateutil import parser, tz

from django.contrib.auth.models import Group, Permission
from django.urls import resolve
from django.http import QueryDict
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.datastructures import MultiValueDict

from django.core.exceptions import FieldError, ValidationError, PermissionDenied

from django.db.models import Q

logger = logging.getLogger(__name__)

LANGUAGE_FORMAL_NAMES = {
    "Albanian": "Albanian",
    "Amharic": "Amharic",
    "Arabic-Mod": "Arabic (Modern Standard)",
    "Arabic Egy": "Arabic (Egyptian)",
    "Arabic-Lev": "Arabic (Levantine)",
    "Azerbaijan": "Azerbaijani",
    "Bengali": "Bengali",
    "Bulgarian": "Bulgarian",
    "Burmese": "Burmese",
    "Cambodian-": "Khmer",
    "Chinese-Ca": "Cantonese",
    "Chinese-Ma": "Mandarin",
    "Czech": "Czech",
    "Danish": "Danish",
    "Dari": "Dari",
    "Dutch": "Dutch",
    "Estonian": "Estonian",
    "Farsi": "Farsi",
    "Finnish": "Finnish",
    "French": "French",
    "Georgian": "Georgian",
    "German": "German",
    "Greek": "Greek",
    "Gujarati": "Gujarati",
    "Haitian Cr": "Haitian Creole",
    "Hausa": "Hausa",
    "Hebrew": "Hebrew",
    "Hindi": "Hindi",
    "Hungarian": "Hungarian",
    "Japanese": "Japanese",
    "Icelandic": "Icelandic",
    "Indonesian": "Indonesian",
    "Italian": "Italian",
    "Kannada": "Kannada",
    "Kazakh": "Kazakh",
    "Kinyarwand": "Kinyarwand",
    "Kirghiz": "Kirghiz",
    "Korean": "Korean",
    "Kurdish": "Kurdish",
    "Kyrgyz": "Kyrgyz",
    "Lao": "Lao",
    "Latvian": "Latvian",
    "Lithuanian": "Lithuanian",
    "Macedonian": "Macedonian",
    "Malay": "Malay",
    "Malayalam": "Malayalam",
    "Mongolian": "Mongolian",
    "Nepali/Nep": "Nepali/Nepalese",
    "Norwegian": "Norwegian",
    "Persian-Ir": "Iranian",
    "Persian-Af": "Afghan",
    "Panjabi/Pu": "Punjabi",
    "Polish": "Polish",
    "Pashto": "Pashto",
    "Portuguese": "Portuguese",
    "Spanish": "Spanish",
    "Armenian-E": "Armenian",
    "Romanian": "Romanian",
    "Russian": "Russian",
    "Serbo-Croa": "Serbo-Croatian (Croatian)",
    "Serbo-Bosn": "Serbo-Croatian (Bosnian)",
    "Serbo-Serb": "Serbo-Croatian (Serbian)",
    "Sindhi": "Sindhi",
    "Singhalese": "Sinhala",
    "Slovak": "Slovakian",
    "Slovenian": "Slovenian",
    "Somali": "Somali",
    "Swahili/Ki": "Swahili",
    "Swati": "Swati",
    "Swedish": "Swedish",
    "Pilipino/T": "Tagalog",
    "Persian -": "Tajiki",
    "Tamil": "Tamil",
    "Telugu": "Telugu",
    "Thai": "Thai",
    "Tibetan": "Tibetan",
    "Turkish": "Turkish",
    "Turkmen": "Turkmen",
    "Ukrainian": "Ukrainian",
    "Urdu": "Urdu",
    "Uzbek": "Uzbek",
    "Vietnamese": "Vietnamese",
}


def resolve_path_to_view(request_path):
    '''
    Returns a viewset if the path resolves to a view
    '''
    # Resolve the path to a view
    view, args, kwargs = resolve(urlparse(request_path)[2])

    # Instantiate the view
    view = view.cls()

    return view


def safe_navigation(object, attribute):
    '''
    Attempts a safe navigation to the specified attribute chain in the object.
    For example, safe_navigation(position, "post.location.country.code") would attempt to return
    the value for position.post.location.country.code, returning "None" if any item in the chain
    does not exist.

    Args:
        - object (Object) - The base object
        - attribute (String) - The dot separated attribute chain

    Returns
        - None - If the attribute chain is broken at some point
        - Value - If the attribute chain is unbroken, the value of object.attribute
    '''
    chain = attribute.split(".")
    try:
        current_object = object
        for link in chain:
            current_object = getattr(current_object, link)
        return current_object
    except AttributeError:
        return None


def get_prefetched_filtered_queryset(model, serializer_class, *args, **kwargs):
    '''
    Gets the model's default queryset, filters by the specified arguments, then
    prefetches the model using the specified serializer class and returns the queryset

    Args:
        - model (Class) - The model for the queryset
        - serializer_class (Class) - The serializer class that supports prefetching
        - *args, **kwargs - Supports filtering of the queryset

    Returns:
        - queryset - The filtered, prefetched queryset
    '''
    queryset = model.objects.filter(*args, **kwargs)
    queryset = serializer_class.prefetch_model(model, queryset)
    return queryset


def ensure_date(date, utc_offset=0):
    '''
    Ensures the date given is a datetime object.

    Args:
        - date (Object or string) - The date

    Returns:
        - date (Object) - Datetime
    '''
    if not date:
        return None
    elif isinstance(date, str):
        return parser.parse(date).astimezone(datetime.timezone.utc) - datetime.timedelta(hours=utc_offset)
    elif isinstance(date, datetime.date):
        return date.astimezone(datetime.timezone(datetime.timedelta(hours=utc_offset)))
    else:
        logger.warn(f"Parameter {date} must be a date object or string")
        return None


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
                elif filter[-2:] == "in" and not isinstance(value, list):
                    value = value.split(",")
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
    query_params = format_filter(filters)

    # Your daily dose of python wizardry: https://docs.python.org/3/library/functions.html#type
    fake_request = type('obj', (object,), {'query_params': query_params})

    # Handles searches on endpoints not backed by database tables
    if getattr(filter_class, "use_api", False):
        queryset = filter_class.get_queryset(query_params)
    else:
        queryset = filter_class.get_subset(query_params)(data=query_params, request=fake_request).qs

    return queryset

def format_filter(filters):
    new_filters = MultiValueDict()

    for key, value in filters.items():
        if isinstance(value, list):
            new_filters.setlist(key, value)
        else:
            new_filters.appendlist(key, value)

    query_params = QueryDict('', mutable=True)
    query_params.update(new_filters)
    return query_params

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


def get_group_by_name(name):
    '''
    Gets the permissions group associated with the specified name

    Args:
        - name (String) - The group name

    Returns
        - Group (object) - The permission group
    '''
    try:
        return Group.objects.get(name=name)
    except Group.DoesNotExist:
        raise Exception(f"Group {name} not found.")


def in_group_or_403(user, group_name):
    '''
    This function mimics the functionality of get_object_or_404, but for permission groups.
    The function accepts a user and group name, doing nothing if the user is present in
    the permission group; otherwise, throws a PermissionDenied error

    Args:
        - user (Object) - The user instance
        - group_name (String) - The name of the permission group
    '''
    try:
        group = get_group_by_name(group_name)
    except:
        raise PermissionDenied
    if group not in user.groups.all():
        raise PermissionDenied


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


def in_superuser_group(user):
    '''
    This function checks whether or not the specified user is in the superuser group

    Args:
        - user (Object) - The user instance
    '''
    try:
        group = get_group_by_name("superuser")
        return group in user.groups.all()
    except:
        return False


def month_diff(start_date, end_date):
    '''
    This function calculates the difference between two dates in months.

    Args:
        - start_date (Date Object) - The start date
        - end_date (Date Object) - The end date

    Returns
        - Integer - The number of months between the dates
    '''

    r = relativedelta(end_date, start_date)
    return r.months + 12 * r.years


def xml_etree_to_dict(tree):
    '''
    Converts an XML etree into a dictionary.

    Args:
        - tree (Object) - XML Element tree

    Returns:
        - Dictionary
    '''

    dictionary = {"children": []}

    for child in tree.iterchildren():
        child_dict = xml_etree_to_dict(child)
        if len(child_dict.keys()) == 2:
            # We are a single tag with a child tag
            if len(child_dict["children"]) == 0:
                del child_dict["children"]
            dictionary = {**dictionary, **child_dict}
        else:
            dictionary["children"].append(xml_etree_to_dict(child))

    dictionary[tree.tag] = tree.text

    return dictionary


def order_dict(dictionary):
    '''
    Orders a dictionary by keys, including nested dictionaries
    '''
    return {k: order_dict(v) if isinstance(v, dict) else v
            for k, v in sorted(dictionary.items())}


def serialize_instance(instance, serializer_string, many=False):
    '''
    Used when performing some look-up logic in a serializer
    Returns the object's serialized data.
    '''
    return locate(serializer_string)(instance, many=many).data
