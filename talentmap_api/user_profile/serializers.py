from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.position.serializers import PositionSerializer

from django.contrib.auth.models import User
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.position.models import Position


class UserSerializer(PrefetchedSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class UserProfileSerializer(PrefetchedSerializer):

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
            "language_qualifications": {
                "class": LanguageQualificationSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True
                }
            },
            "favorite_positions": {
                "class": PositionSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "representation"
                    ],
                    "many": True,
                    "read_only": True
                }
            }
        }


class UserProfileWritableSerializer(PrefetchedSerializer):

    def validate(self, data):
        '''
        Validate user profile here, mainly position preferences as this is an
        arbitrary json object
        '''
        if 'position_preferences' in data:
            # Verify that position preferences are a valid set of position filters
            try:
                Position.objects.filter(Q(**data.get('position_preferences')))
            except:
                raise ValidationError("Position preferences must be a valid set of position filters")

        return data

    class Meta:
        model = UserProfile
        fields = "__all__"
