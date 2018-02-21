from rest_framework import serializers

from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField

from talentmap_api.common.common_helpers import get_group_by_name

from talentmap_api.position.models import Position, Grade, Skill, SkillCone, CapsuleDescription, Classification, Assignment, PositionBidStatistics
from talentmap_api.language.serializers import LanguageQualificationSerializer
from talentmap_api.organization.serializers import PostSerializer


class CapsuleDescriptionSerializer(PrefetchedSerializer):
    last_editing_user = StaticRepresentationField(read_only=True)

    # This is a dynamic flag used by the front end to simplify checking if the current user has permissions
    is_editable_by_user = serializers.SerializerMethodField()

    date_created = serializers.DateTimeField(read_only=True)
    date_updated = serializers.DateTimeField(read_only=True)

    def get_is_editable_by_user(self, obj):
        try:
            # RC-1 inform UI of superuser status
            try:  # nosec
                if get_group_by_name("superuser") in self.context.get("request").user.groups.all():
                    return True
            except:
                pass  # No super user group
            return self.context.get("request").user.has_perm(f"position.{obj.position.post.permission_edit_post_capsule_description_codename}")
        except AttributeError:
            # The position doesn't have a post, or otherwise
            return False

    class Meta:
        model = CapsuleDescription
        fields = "__all__"
        writable_fields = ("content", "point_of_contact", "website",)


class CurrentAssignmentSerializer(PrefetchedSerializer):
    user = StaticRepresentationField(read_only=True)
    tour_of_duty = StaticRepresentationField(read_only=True)

    class Meta:
        model = Assignment
        exclude = ("position",)


class AssignmentSerializer(CurrentAssignmentSerializer):

    class Meta:
        model = Assignment
        fields = "__all__"
        nested = {
            "position": {
                "class": "talentmap_api.position.serializers.PositionSerializer",
                "field": "position",
                "kwargs": {
                    "override_fields": [
                        "position_number",
                        "bureau",
                        "skill",
                        "title",
                        "post__location",
                    ],
                    "read_only": True
                }
            }
        }


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
    bidcycle = StaticRepresentationField(read_only=True)

    class Meta:
        model = PositionBidStatistics
        exclude = ("position",)


class PositionSerializer(PrefetchedSerializer):
    grade = StaticRepresentationField(read_only=True)
    skill = StaticRepresentationField(read_only=True)
    bureau = serializers.SerializerMethodField()
    organization = serializers.SerializerMethodField()
    classifications = StaticRepresentationField(read_only=True, many=True)
    representation = serializers.SerializerMethodField()

    # This method returns the string representation of the bureau, or the code
    # if it doesn't currently exist in the database
    def get_bureau(self, obj):
        if obj.bureau:
            return obj.bureau._string_representation
        else:
            return obj._bureau_code

    # This method returns the string representation of the parent org, or the code
    # if it doesn't currently exist in the database
    def get_organization(self, obj):
        if obj.organization:
            return obj.organization._string_representation
        else:
            return obj._org_code

    class Meta:
        model = Position
        fields = "__all__"
        nested = {
            "bid_statistics": {
                "class": PositionBidStatisticsSerializer,
                "kwargs": {
                    "many": True,
                    "read_only": True
                }
            },
            "languages": {
                "class": LanguageQualificationSerializer,
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
                "class": CurrentAssignmentSerializer,
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
    cone = StaticRepresentationField(read_only=True)

    class Meta:
        model = Skill
        fields = "__all__"


class SkillConeSerializer(PrefetchedSerializer):
    skills = StaticRepresentationField(read_only=True, many=True)

    class Meta:
        model = SkillCone
        fields = "__all__"
