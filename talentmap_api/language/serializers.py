from rest_framework import serializers

from talentmap_api.language.models import Language, Proficiency, Qualification


class LanguageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Language
        fields = "__all__"


class LanguageProficiencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Proficiency
        fields = "__all__"


class LanguageQualificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Qualification
        fields = "__all__"
