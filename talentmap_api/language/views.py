from rest_framework.viewsets import ReadOnlyModelViewSet

from talentmap_api.language.models import Language, Proficiency, Qualification


class LanguageListView(ReadOnlyModelViewSet):
    """
    Lists all available languages.
    """

    serializer_class = LanguageSerializer

    def get_queryset(self):
        return Language.objects.all()


class LanguageProficiencyListView(ReadOnlyModelViewSet):
    """
    Lists all available languages.
    """

    serializer_class = LanguageProficiencySerializer

    def get_queryset(self):
        return Proficiency.objects.all()


class LanguageQualificationListView(ReadOnlyModelViewSet):
    """
    Lists all available languages.
    """

    serializer_class = LanguageQualificationSerializer

    def get_queryset(self):
        return Qualification.objects.all()
