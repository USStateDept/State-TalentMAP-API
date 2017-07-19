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
    favorite_positions = serializers.StringRelatedField(many=True)
    language_qualifications = serializers.StringRelatedField(many=True)

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
        fields = "__all__"
