from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.language.models import Language, Proficiency, Qualification
from talentmap_api.language.serializers import LanguageSerializer, LanguageProficiencySerializer, LanguageQualificationSerializer
from talentmap_api.language.filters import LanguageFilter, ProficiencyFilter, QualificationFilter


class LanguageListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given language.

    list:
    Return a list of all languages.
    """

    serializer_class = LanguageSerializer
    filter_class = LanguageFilter

    def get_queryset(self):
        return Language.objects.all()


class LanguageProficiencyListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given proficiency.

    list:
    Return a list of all proficiencies.
    """

    serializer_class = LanguageProficiencySerializer
    filter_class = ProficiencyFilter

    def get_queryset(self):
        return Proficiency.objects.all()


class LanguageQualificationListView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the given qualification.

    list:
    Return a list of all qualifications.
    """

    serializer_class = LanguageQualificationSerializer
    filter_class = QualificationFilter

    def get_queryset(self):
        return Qualification.objects.all()
