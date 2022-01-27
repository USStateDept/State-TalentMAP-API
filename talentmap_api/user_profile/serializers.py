import logging

from django.http import QueryDict
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
from rest_framework import serializers

from talentmap_api.common.common_helpers import resolve_path_to_view, validate_filters_exist, serialize_instance
from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.available_positions.models import AvailablePositionFavorite
from talentmap_api.fsbid.services.cdo import single_cdo
from talentmap_api.user_profile.models import UserProfile, SavedSearch
from talentmap_api.fsbid.services.available_positions import get_available_positions
from talentmap_api.fsbid.services.employee import get_employee_information
from talentmap_api.fsbid.services.client import get_user_information, fsbid_clients_to_talentmap_clients
from talentmap_api.fsbid.services.common import get_fsbid_results

logger = logging.getLogger(__name__)

CLIENTS_ROOT_V2 = settings.CLIENTS_API_V2_URL


class UserSerializer(PrefetchedSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class UserProfilePublicSerializer(PrefetchedSerializer):
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    user_info = serializers.SerializerMethodField()

    def get_user_info(self, obj):
        request = self.context['request']
        try:
            jwt = request.META['HTTP_JWT']
            user = UserProfile.objects.get(user=request.user)
            return get_user_information(jwt, user.emp_id)
        except BaseException:
            return {}

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "email", "user_info"]


class UserProfileShortSerializer(PrefetchedSerializer):
    is_cdo = serializers.ReadOnlyField()
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    initials = serializers.ReadOnlyField()
    avatar = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ["username", "first_name", "last_name", "email", "is_cdo", "initials", "avatar", "display_name"]


class ClientSerializer(PrefetchedSerializer):
    grade = StaticRepresentationField(read_only=True)
    is_cdo = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()
    avatar = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ["id", "skills", "grade", "is_cdo", "bid_statistics", "user", "initials", "avatar", "display_name"]
        nested = {
            "user": {
                "class": UserSerializer,
                "kwargs": {
                    "read_only": True
                }
            }
        }


class ClientDetailSerializer(ClientSerializer):
    pass


class UserProfileSerializer(PrefetchedSerializer):
    cdo = StaticRepresentationField(read_only=True)
    is_cdo = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()
    avatar = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    # Use cdo_info so we don't have to break legacy CDO functionality
    cdo_info = serializers.SerializerMethodField()
    employee_info = serializers.SerializerMethodField()
    user_info = serializers.SerializerMethodField()
    current_assignment = serializers.SerializerMethodField()

    def get_favorite_positions(self, obj):
        request = self.context['request']
        user = UserProfile.objects.get(user=request.user)
        aps = AvailablePositionFavorite.objects.filter(user=user).values_list("cp_id", flat=True)
        if len(aps) > 0:
            pos_nums = ','.join(aps)
            aps = get_available_positions(QueryDict(f"id={pos_nums}"), request.META['HTTP_JWT'])["results"]
            return ({'id': o['id']} for o in aps)
        return []

    def get_cdo_info(self, obj):
        request = self.context['request']
        try:
            jwt = request.META['HTTP_JWT']
            user = UserProfile.objects.get(user=request.user)
            return single_cdo(jwt, user.emp_id)
        except BaseException:
            return {}

    def get_employee_info(self, obj):
        request = self.context['request']
        try:
            jwt = request.META['HTTP_JWT']
            user = UserProfile.objects.get(user=request.user)
            return get_employee_information(jwt, user.emp_id)
        except BaseException:
            return {}

    def get_user_info(self, obj):
        request = self.context['request']
        try:
            jwt = request.META['HTTP_JWT']
            user = UserProfile.objects.get(user=request.user)
            return get_user_information(jwt, user.emp_id)
        except BaseException:
            return {}

    def get_current_assignment(self, obj):
        request = self.context['request']
        try:
            jwt = request.META['HTTP_JWT']
            user = UserProfile.objects.get(user=request.user)
            perdet = user.emp_id
            if not perdet:
                return {}

            uriCurrentAssignment = f"?request_params.perdet_seq_num={perdet}&request_params.currentAssignmentOnly=true"
            responseCurrentAssignment = get_fsbid_results(uriCurrentAssignment, jwt, fsbid_clients_to_talentmap_clients, None, False, CLIENTS_ROOT_V2)
            return list(responseCurrentAssignment)[0].get('current_assignment', {})
        except BaseException:
            return {}

    class Meta:
        model = UserProfile
        fields = "__all__"
        nested = {
            "user": {
                "class": UserSerializer,
                "kwargs": {
                    "read_only": True
                }
            }
        }


class UserProfileWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = UserProfile
        fields = ["initials", "avatar", "display_name"]
        writable_fields = ()


class SavedSearchSerializer(PrefetchedSerializer):
    owner = serializers.StringRelatedField(read_only=True)

    def save(self, **kwargs):
        super().save(owner=kwargs['owner'])
        self.instance.update_count(True, kwargs['jwt_token'])

    def validate(self, data):
        # We'll need the endpoint to validate our filters, so determine if our
        # datasource is an instance or a fresh object (in which case we use initial data)
        datasource = self.initial_data
        if self.instance:
            datasource = self.instance.__dict__

        # The endpoint to test our filters against is either the one stored, or the incoming endpoint
        endpoint = data.get("endpoint", datasource.get("endpoint"))
        # Likewise for the filters
        filters = data.get("filters", datasource.get("filters"))

        # Get our viewset using the endpoint
        try:
            view = resolve_path_to_view(endpoint)
        except BaseException:
            view = None
        finally:
            if not view:
                # Raise a validation error if the endpoint isn't good
                raise ValidationError(f"Endpoint {endpoint} is not a valid API path")

        """
        Disabling validation, as the benefit is negligible and requires us to keep the
        allowed fields up to date with FSBid API.
        """
        # Get our list of filters, and verify that the specified filters are valid
        # if hasattr(view, "filter_class"):
        #    validate_filters_exist(filters, view.filter_class)
        # else:
        #    raise ValidationError("Specified endpoint does not support filters")

        return data

    class Meta:
        model = SavedSearch
        fields = "__all__"
        writable_fields = ("name", "endpoint", "filters", "is_bureau")
