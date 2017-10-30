from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer

from talentmap_api.position.models import Position, Grade, Skill, CapsuleDescription, Classification, Assignment, PositionBidStatistics
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.organization.serializers import PostSerializer


class CapsuleDescriptionSerializer(PrefetchedSerializer):
    last_editing_user = serializers.StringRelatedField(read_only=True)

    # This is a dynamic flag used by the front end to simplify checking if the current user has permissions
    is_editable_by_user = serializers.SerializerMethodField()

    date_created = serializers.DateTimeField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)

    def get_is_editable_by_user(self, obj):
        try:
            return self.context.get("request").user.has_perm(f"position.{self.post.permission_edit_post_capsule_description_codename}")
        except AttributeError:
            # The position doesn't have a post, or otherwise
            return False

    class Meta:
        model = CapsuleDescription
        fields = "__all__"
        writable_fields = ("content", "point_of_contact", "website",)


class AssignmentSerializer(PrefetchedSerializer):
    user = serializers.StringRelatedField()
    position = serializers.StringRelatedField()
    tour_of_duty = serializers.StringRelatedField()

    class Meta:
        model = Assignment
        fields = "__all__"


class ClassificationSerializer(PrefetchedSerializer):

    class Meta:
        model = Classification
        fields = "__all__"


class PositionWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = Position
        fields = ("classifications",)
        writable_fields = ("classifications",)


class PositionBidStatisticsSerializer(PrefetchedSerializer):
    # We'll want to serialize this as text once the representation tech debt story is complete
    # bidcycle = serializers.StringRelatedField()

    class Meta:
        model = PositionBidStatistics
        exclude = ("position",)


class PositionSerializer(PrefetchedSerializer):
    grade = serializers.StringRelatedField()
    skill = serializers.StringRelatedField()
    bureau = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    representation = serializers.SerializerMethodField()
    classifications = serializers.StringRelatedField(many=True)

    def get_representation(self, obj):
        return str(obj)

    # This method returns the string representation of the bureau, or the code
    # if it doesn't currently exist in the database
    def get_bureau(self, obj):
        if obj.bureau:
            return str(obj.bureau)
        else:
            return obj._bureau_code

    # This method returns the string representation of the parent org, or the code
    # if it doesn't currently exist in the database
    def get_organization(self, obj):
        if obj.organization:
            return str(obj.organization)
        else:
            return obj._org_code

    class Meta:
        model = Position
        fields = "__all__"
        nested = {
            "bid_statistics": {
                "class": PositionBidStatisticsSerializer,
                "field": "bid_statistics",
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "languages": {
                "class": LanguageQualificationSerializer,
                "field": "language_requirements",
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "post": {
                "class": PostSerializer,
                "field": "post",
                "kwargs": {
                    "many": False,
                    "read_only": True
                }
            },
            "description": {
                "class": CapsuleDescriptionSerializer,
                "field": "description",
                "kwargs": {
                    "read_only": True
                }
            },
            "current_assignment": {
                "class": AssignmentSerializer,
                "field": "current_assignment",
                "kwargs": {
                    "override_fields": [
                        "user",
                        "status",
                        "start_date",
                        "tour_of_duty",
                        "estimated_end_date"
                    ],
                    "read_only": True
                }
            }
        }


class GradeSerializer(PrefetchedSerializer):

    class Meta:
        model = Grade
        fields = ("id", "code")


class SkillSerializer(PrefetchedSerializer):

    class Meta:
        model = Skill
        fields = "__all__"
