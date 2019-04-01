from talentmap_api.common.serializers import PrefetchedSerializer, StaticRepresentationField
from talentmap_api.language.models import Language, Proficiency, Qualification


class LanguageSerializer(PrefetchedSerializer):

    formal_description = StaticRepresentationField(read_only=True)

    class Meta:
        model = Language
        fields = "__all__"


class LanguageProficiencySerializer(PrefetchedSerializer):

    class Meta:
        model = Proficiency
        fields = "__all__"


class LanguageQualificationSerializer(PrefetchedSerializer):

    language = StaticRepresentationField(read_only=True)
    reading_proficiency = StaticRepresentationField(read_only=True)
    spoken_proficiency = StaticRepresentationField(read_only=True)
    representation = StaticRepresentationField(read_only=True, source="_string_representation")

    class Meta:
        model = Qualification
        fields = "__all__"


class LanguageQualificationWritableSerializer(PrefetchedSerializer):

    class Meta:
        model = Qualification
        fields = "__all__"
        writable_fields = ("language", "reading_proficiency", "spoken_proficiency")
