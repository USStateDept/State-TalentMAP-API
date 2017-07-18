from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.position.serializers import PositionSerializer

from django.contrib.auth.models import User
from talentmap_api.user_profile.models import UserProfile


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
                    "many": True,
                    "read_only": True
                }
            },
            "favorite_positions": {
                "class": PositionSerializer,
                "kwargs": {
                    "override_fields": [
                        "id",
                        "position_number",
                        "title",
                        "post",
                        "post__description"
                    ],
                    "many": True,
                    "read_only": True
                }
            }
        }


class UserProfileWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = UserProfile
        fields = "__all__"
