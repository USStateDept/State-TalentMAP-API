from django.core.exceptions import ValidationError
from django.db.models import Q
from django.apps import apps
from rest_framework import serializers
from rest_framework.reverse import reverse

from talentmap_api.common.serializers import PrefetchedSerializer
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.position.serializers import PositionSerializer

from django.contrib.auth.models import User
from talentmap_api.user_profile.models import UserProfile, Sharable
from talentmap_api.position.models import Position


class UserSerializer(PrefetchedSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]


class SharableSerializer(PrefetchedSerializer):
    sharing_user = serializers.StringRelatedField()
    receiving_user = serializers.StringRelatedField()

    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        model = apps.get_model(obj.sharable_model)
        instance = model.objects.get(id=obj.sharable_id)

        return {
            "representation": f"{instance}",
            "url": reverse(f'view-{obj.sharable_model}-details', kwargs={"pk": obj.sharable_id}, request=self.context.get("request"))
        }

    class Meta:
        model = Sharable
        fields = ["id", "sharing_user", "receiving_user", "content", "read"]


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
            },
            "received_shares": {
                "class": SharableSerializer,
                "kwargs": {
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
