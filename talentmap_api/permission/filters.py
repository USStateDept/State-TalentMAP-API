import rest_framework_filters as filters

from django.contrib.auth.models import Group, Permission

from talentmap_api.common.filters import full_text_search
from talentmap_api.common.filters import ALL_TEXT_LOOKUPS, INTEGER_LOOKUPS, FOREIGN_KEY_LOOKUPS


class PermissionFilter(filters.FilterSet):

    q = filters.CharFilter(name="name", method=full_text_search(
        fields=[
            "name",
            "codename"
        ]
    ))

    class Meta:
        model = Permission
        fields = {
            "id": INTEGER_LOOKUPS,
            "name": ALL_TEXT_LOOKUPS,
            "codename": ALL_TEXT_LOOKUPS
        }


class GroupFilter(filters.FilterSet):
    permissions = filters.RelatedFilter(PermissionFilter, name='permissions', queryset=Permission.objects.all())

    q = filters.CharFilter(name="name", method=full_text_search(
        fields=[
            "name",
            "permissions__name",
            "permissions__codename"
        ]
    ))

    class Meta:
        model = Group
        fields = {
            "id": INTEGER_LOOKUPS,
            "name": ALL_TEXT_LOOKUPS,
            "permissions": FOREIGN_KEY_LOOKUPS
        }
