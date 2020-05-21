from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.common_helpers import get_prefetched_filtered_queryset
from talentmap_api.common.mixins import FieldLimitableSerializerMixin, ActionDependentSerializerMixin

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.filters import ClientFilter
from talentmap_api.user_profile.serializers import ClientSerializer, ClientDetailSerializer
