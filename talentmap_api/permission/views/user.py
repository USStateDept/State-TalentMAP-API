from rest_framework.viewsets import ViewSet, GenericViewSet
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.permission.serializers import UserPermissionSerializer
from talentmap_api.user_profile.serializers import UserSerializer
from talentmap_api.user_profile.models import UserProfile


def construct_return_object(user):
    permission_dict = {}
    permission_dict["user"] = UserSerializer(user).data
    permission_dict["groups"] = list(user.groups.values_list("name", flat=True))
    permission_dict["permissions"] = list(user.get_all_permissions())
    return permission_dict


class UserPermissionView(FieldLimitableSerializerMixin,
                         ViewSet):
    """
    list:
    Return a list of the current user's permissions.
    """

    def list(self, request, format=None):
        return Response(construct_return_object(request.user),
                        status=status.HTTP_200_OK)


class AllUserPermissionView(FieldLimitableSerializerMixin,
                            GenericViewSet,
                            mixins.ListModelMixin):
    """
    list:
    Return a list of the users and their permissions.

    retrieve:
    Return the specified user's permissions by profile ID.
    """
    serializer_class = UserPermissionSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('superuser'))

    def retrieve(self, request, pk=None, format=None):
        profile = get_object_or_404(UserProfile, id=request.parser_context.get("kwargs").get("pk"))
        return Response(construct_return_object(profile.user),
                        status=status.HTTP_200_OK)

    def get_queryset(self):
        ordering = self.request.query_params.get('sort', '')
        filtering = self.request.query_params.get('filters', [])
        username_filter = self.request.query_params.get('q_username', '')
        name_filter = self.request.query_params.get('q_name', '')

        fields = {}

        if filtering:
            filters = [x for x in filtering.split(',')]
            fields['groups__in'] = filters

        if username_filter:
            fields['username__icontains'] = username_filter

        if ordering:
            queryset = User.objects.all().order_by(ordering).filter(**fields)
        else:
            queryset = User.objects.all().filter(**fields)

        if name_filter:
            queryset = queryset.filter(Q(first_name__icontains=name_filter) | Q(last_name__icontains=name_filter))

        queryset = self.serializer_class.prefetch_model(User, queryset)
        return queryset
