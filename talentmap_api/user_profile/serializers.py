from django.core.exceptions import ValidationError
from rest_framework import serializers

from talentmap_api.common.common_helpers import resolve_path_to_view, validate_filters_exist, serialize_instance
from talentmap_api.bidding.serializers.serializers import UserBidStatisticsSerializer, CyclePositionSerializer
from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.position.serializers import PositionSerializer, SkillSerializer, CurrentAssignmentSerializer
from talentmap_api.messaging.serializers import SharableSerializer

from django.contrib.auth.models import User
from talentmap_api.user_profile.models import UserProfile, SavedSearch


class UserSerializer(PrefetchedSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class UserProfilePublicSerializer(PrefetchedSerializer):
    current_assignment = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")

    def get_current_assignment(self, obj):
        if obj.assignments.count() > 0:
            return str(obj.assignments.latest('start_date'))
        else:
            return None

    class Meta:
        model = UserProfile
        fields = ["first_name", "last_name", "email", "current_assignment", "skills"]
        nested = {
            "skills": {
                "class": SkillSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }


class UserProfileShortSerializer(PrefetchedSerializer):
    is_cdo = serializers.ReadOnlyField()
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.CharField(source="user.email")
    initials = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ["username", "first_name", "last_name", "email", "phone_number", "is_cdo", "initials", "display_name"]


class ClientSerializer(PrefetchedSerializer):
    current_assignment = serializers.SerializerMethodField()
    grade = StaticRepresentationField(read_only=True)
    is_cdo = serializers.ReadOnlyField()
    primary_nationality = StaticRepresentationField(read_only=True)
    secondary_nationality = StaticRepresentationField(read_only=True)
    initials = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()

    def get_current_assignment(self, obj):
        if obj.assignments.count() > 0:
            return str(obj.assignments.latest('start_date'))
        else:
            return None

    def get_assignment(self, obj):
        if obj.assignments.count() > 0:
            return str(obj.assignments.latest('start_date'))
        else:
            return None

    class Meta:
        model = UserProfile
        fields = ["id", "current_assignment", "assignments", "skills", "grade", "is_cdo", "primary_nationality", "secondary_nationality", "bid_statistics", "user", "language_qualifications", "initials", "display_name"]
        nested = {
            "user": {
                "class": UserSerializer,
                "kwargs": {
                    "read_only": True
                }
            },
            "language_qualifications": {
                "class": LanguageQualificationSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True,
                }
            },
            "bid_statistics": {
                "class": UserBidStatisticsSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "skills": {
                "class": SkillSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "assignments": {
                "class": CurrentAssignmentSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }


class ClientDetailSerializer(ClientSerializer):

    def get_current_assignment(self, obj):
        if obj.assignments.count() > 0:
            return serialize_instance(obj.assignments.latest('start_date'), "talentmap_api.position.serializers.AssignmentSerializer")
        else:
            return None


class UserProfileSerializer(PrefetchedSerializer):
    current_assignment = serializers.SerializerMethodField()
    skills = StaticRepresentationField(read_only=True, many=True)
    grade = StaticRepresentationField(read_only=True)
    cdo = StaticRepresentationField(read_only=True)
    is_cdo = serializers.ReadOnlyField()
    initials = serializers.ReadOnlyField()
    primary_nationality = StaticRepresentationField(read_only=True)
    secondary_nationality = StaticRepresentationField(read_only=True)
    display_name = serializers.ReadOnlyField()

    def get_current_assignment(self, obj):
        if obj.assignments.count() > 0:
            return str(obj.assignments.latest('start_date'))
        else:
            return None

    class Meta:
        model = UserProfile
        fields = "__all__"
        nested = {
            "user": {
                "class": UserSerializer,
                "kwargs": {
                    "read_only": True
                }
            },
            "cdo": {
                "class": UserProfileShortSerializer,
                "kwargs": {
                    "read_only": True
                }
            },
            "language_qualifications": {
                "class": LanguageQualificationSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True,
                }
            },
            "favorite_positions": {
                "class": CyclePositionSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True
                }
            },
            "received_shares": {
                "class": SharableSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "skills": {
                "class": SkillSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            }
        }


class UserProfileWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = UserProfile
        fields = ["language_qualifications", "favorite_positions", "primary_nationality", "secondary_nationality", "date_of_birth", "phone_number", "initials", "display_name"]
        writable_fields = ("language_qualifications", "favorite_positions", "primary_nationality", "secondary_nationality", "date_of_birth", "phone_number")


class SavedSearchSerializer(PrefetchedSerializer):
    owner = serializers.StringRelatedField(read_only=True)

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
        except:
            view = None
        finally:
            if not view:
                # Raise a validation error if the endpoint isn't good
                raise ValidationError(f"Endpoint {endpoint} is not a valid API path")

        # Get our list of filters, and verify that the specified filters are valid
        if hasattr(view, "filter_class"):
            validate_filters_exist(filters, view.filter_class)
        else:
            raise ValidationError("Specified endpoint does not support filters")

        return data

    class Meta:
        model = SavedSearch
        fields = "__all__"
        writable_fields = ("name", "endpoint", "filters",)
