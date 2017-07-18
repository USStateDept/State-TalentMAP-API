from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.language.serializers import LanguageQualificationSerializer

from django.contrib.auth.models import User
from talentmap_api.user_profile.models import UserProfile


class UserSerializer(serializers.ModelSerializer):
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
        }
