import coreapi
import maya
import logging
import pydash

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.shortcuts import get_object_or_404
from django.http import QueryDict
from django.db.models.functions import Concat
from django.db.models import TextField
from django.conf import settings

from rest_framework.viewsets import GenericViewSet
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework_bulk import (
    ListBulkCreateUpdateDestroyAPIView,
)

from rest_condition import Or

from talentmap_api.common.common_helpers import in_group_or_403, get_prefetched_filtered_queryset
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.available_positions.models import AvailablePositionFavorite, AvailablePositionDesignation, AvailablePositionRanking, AvailablePositionRankingLock
from talentmap_api.available_positions.serializers.serializers import AvailablePositionDesignationSerializer, AvailablePositionRankingSerializer, AvailablePositionRankingLockSerializer
from talentmap_api.available_positions.filters import AvailablePositionRankingFilter, AvailablePositionRankingLockFilter
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

import talentmap_api.fsbid.services.available_positions as services
import talentmap_api.fsbid.services.projected_vacancies as pvservices
import talentmap_api.fsbid.services.common as comservices
import talentmap_api.fsbid.services.employee as empservices
import talentmap_api.fsbid.services.bid as bidservices

logger = logging.getLogger(__name__)

FAVORITES_LIMIT = settings.FAVORITES_LIMIT


class AvailablePositionsFilter():
    declared_filters = [
        "exclude_available",
        "exclude_projected",
    ]

    use_api = True

    class Meta:
        fields = "__all__"


class AvailablePositionFavoriteListView(APIView):

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.')
        ])

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the user's favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailablePositionFavorite.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        limit = request.query_params.get('limit', 15)
        page = request.query_params.get('page', 1)
        ordering = request.query_params.get('ordering', None)
        if len(aps) > 0:
            comservices.archive_favorites(aps, request)
            pos_nums = ','.join(aps)
            return Response(services.get_available_positions(QueryDict(f"id={pos_nums}&limit={limit}&page={page}&ordering={ordering}"),
                                                             request.META['HTTP_JWT'],
                                                             f"{request.scheme}://{request.get_host()}"))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})


class AvailablePositionFavoriteIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the user's favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailablePositionFavorite.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        return Response(aps)


class AvailablePositionRankingView(FieldLimitableSerializerMixin,
                                   GenericViewSet,
                                   ListBulkCreateUpdateDestroyAPIView,
                                   mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin):

    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('bureau_user'), isDjangoGroupMember('post_user')), ]
    serializer_class = AvailablePositionRankingSerializer
    filter_class = AvailablePositionRankingFilter

    # For all requests, if the position is locked, then the user must have the appropriate bureau permission for the cp_id

    def perform_create(self, serializer):
        if isinstance(self.request.data, list):
            data = self.request.data
            # Empty array
            if len(data) == 0:
                raise SuspiciousOperation('Array is empty')
            cp = data[0].get('cp_id')
            # All cp_id values must match the first one
            if not all(x.get('cp_id') == data[0].get('cp_id') for x in data):
                raise SuspiciousOperation('All cp_id values must be identical')
        # if a single object is passed
        if isinstance(self.request.data, dict):
            cp = self.request.data.get('cp_id')

        hasBureauPermissions = empservices.has_bureau_permissions(cp, self.request.META['HTTP_JWT'])
        hasOrgPermissions = empservices.has_org_permissions(cp, self.request.META['HTTP_JWT'])
        exists = AvailablePositionRankingLock.objects.filter(cp_id=cp).exists()

        # is locked and does not have bureau permissions
        if exists and not hasBureauPermissions:
            raise PermissionDenied()
        # not locked and (has org permission or bureau permission)
        if not exists and (hasOrgPermissions or hasBureauPermissions):
            serializer.save(user=self.request.user.profile)
        elif exists and hasBureauPermissions:
            serializer.save(user=self.request.user.profile)
        else:
            raise PermissionDenied()

    def get_queryset(self):
        cp = self.request.GET.get('cp_id')
        hasBureauPermissions = empservices.has_bureau_permissions(cp, self.request.META['HTTP_JWT'])
        hasOrgPermissions = empservices.has_org_permissions(cp, self.request.META['HTTP_JWT'])

        if hasOrgPermissions or hasBureauPermissions:
            return get_prefetched_filtered_queryset(AvailablePositionRanking, self.serializer_class).order_by('rank')
        # doesn't have permission
        raise PermissionDenied()

    def perform_delete(self, request, pk, format=None):
        '''
        Removes the available position rankings by cp_id for the user
        '''
        cp = pk
        hasBureauPermissions = empservices.has_bureau_permissions(cp, self.request.META['HTTP_JWT'])
        hasOrgPermissions = empservices.has_org_permissions(cp, self.request.META['HTTP_JWT'])
        exists = AvailablePositionRankingLock.objects.filter(cp_id=cp).exists()

        # is locked and does not have bureau permissions
        if exists and not hasBureauPermissions:
            return Response(status=status.HTTP_403_FORBIDDEN)
        # not locked and (has org permission or bureau permission)
        elif not exists and (hasOrgPermissions or hasBureauPermissions):
            get_prefetched_filtered_queryset(AvailablePositionRanking, self.serializer_class, cp_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif exists and hasBureauPermissions:
            get_prefetched_filtered_queryset(AvailablePositionRanking, self.serializer_class, cp_id=pk).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        # doesn't have permission
        return Response(status=status.HTTP_403_FORBIDDEN)

class AvailablePositionRankingLockView(FieldLimitableSerializerMixin,
                                       GenericViewSet,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin):

    permission_classes = (IsAuthenticated,)
    serializer_class = AvailablePositionRankingLockSerializer
    filter_class = AvailablePositionRankingLockFilter


    def put(self, request, pk, format=None):
        # must have bureau permission for the bureau code associated with the position
        if not empservices.has_bureau_permissions(pk, request.META['HTTP_JWT']):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # get the bureau code and org code associated with the position
        pos = services.get_available_position(pk, request.META['HTTP_JWT'])
        try:
            bureau = pos.get('position').get('bureau_code')
            org = pos.get('position').get('organization_code')
        # return a 404 if we can't determine the bureau/org code
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if pos is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # if the position is already locked, still update the bureau/org codes
        if AvailablePositionRankingLock.objects.filter(cp_id=pk).exists():
            AvailablePositionRankingLock.objects.filter(cp_id=pk).update(bureau_code=bureau, org_code=org)
            return Response(status=status.HTTP_204_NO_CONTENT)

        # save the cp_id, bureau code and org code
        position, _ = AvailablePositionRankingLock.objects.get_or_create(cp_id=pk, bureau_code=bureau, org_code=org)
        position.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get(self, request, pk, format=None):
        '''
        Indicates if the available position is locked

        Returns 204 if the available position is locked, otherwise, 404
        '''
        # must have bureau permission for the bureau code associated with the position
        if not empservices.has_bureau_permissions(pk, request.META['HTTP_JWT']) and not empservices.has_org_permissions(pk, self.request.META['HTTP_JWT']):
            return Response(status=status.HTTP_403_FORBIDDEN)

        if AvailablePositionRankingLock.objects.filter(cp_id=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        '''
        Removes the available position ranking by cp_id
        '''
        # must have bureau permission for the bureau code associated with the position
        if not empservices.has_bureau_permissions(pk, request.META['HTTP_JWT']):
            return Response(status=status.HTTP_403_FORBIDDEN)

        get_prefetched_filtered_queryset(AvailablePositionRankingLock, self.serializer_class, cp_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoritesCSVView(APIView):

    permission_classes = (IsAuthenticated,)
    filter_class = AvailablePositionsFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('exclude_available', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Whether to exclude available positions'),
            openapi.Parameter('exclude_projected', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Whether to exclude projected vacancies')
        ])

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the user's favorite positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        data = []

        aps = AvailablePositionFavorite.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        if len(aps) > 0 and request.query_params.get('exclude_available') != 'true':
            pos_nums = ','.join(aps)
            apdata = services.get_available_positions(QueryDict(f"id={pos_nums}&limit={len(aps)}&page=1"), request.META['HTTP_JWT'])
            data = data + apdata.get('results')

        pvs = ProjectedVacancyFavorite.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        if len(pvs) > 0 and request.query_params.get('exclude_projected') != 'true':
            pos_nums = ','.join(pvs)
            pvdata = pvservices.get_projected_vacancies(QueryDict(f"id={pos_nums}&limit={len(pvs)}&page=1"), request.META['HTTP_JWT'])
            data = data + pvdata.get('results')

        return comservices.get_ap_and_pv_csv(data, "favorites", True)


class AvailablePositionFavoriteActionView(APIView):
    '''
    Controls the favorite status of a available position

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the available position is a favorite

        Returns 204 if the available position is a favorite, otherwise, 404
        '''
        user = UserProfile.objects.get(user=self.request.user)
        if AvailablePositionFavorite.objects.filter(user=user, cp_id=pk, archived=False).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the available position as a favorite
        '''
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailablePositionFavorite.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        comservices.archive_favorites(aps, request)
        aps_after_archive = AvailablePositionFavorite.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        if len(aps_after_archive) >= FAVORITES_LIMIT:
            return Response({"limit": FAVORITES_LIMIT}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        else:
            AvailablePositionFavorite.objects.get_or_create(user=user, cp_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the available position from favorites
        '''
        user = UserProfile.objects.get(user=self.request.user)
        AvailablePositionFavorite.objects.filter(user=user, cp_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailablePositionDesignationView(mixins.UpdateModelMixin,
                                       FieldLimitableSerializerMixin,
                                       GenericViewSet):
    '''
    partial_update:
    Updates an available position designation
    '''
    serializer_class = AvailablePositionDesignationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = AvailablePositionDesignation.objects.all()
        queryset = self.serializer_class.prefetch_model(AvailablePositionDesignation, queryset)
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        pk = self.kwargs.get('pk', None)
        obj, _ = queryset.get_or_create(cp_id=pk)
        self.check_object_permissions(self.request, obj)
        return obj


class AvailablePositionHighlightListView(APIView):
    """
    list:
    Return a list of all currently highlighted available positions
    """

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the higlighted available positions.
        """
        cp_ids = AvailablePositionDesignation.objects.filter(is_highlighted=True).values_list("cp_id", flat=True)
        if len(cp_ids) > 0:
            pos_nums = ','.join(cp_ids)
            return Response(services.get_available_positions(QueryDict(f"id={pos_nums}"), request.META['HTTP_JWT']))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})


class AvailablePositionHighlightActionView(APIView):
    '''
    Controls the highlighted status of an available position
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the position is highlighted

        Returns 204 if the position is highlighted, otherwise, 404
        '''
        position = get_object_or_404(AvailablePositionDesignation, cp_id=pk)
        if position.is_highlighted is True:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the position as highlighted by the position's bureau
        '''
        position, _ = AvailablePositionDesignation.objects.get_or_create(cp_id=pk)
        in_group_or_403(self.request.user, "superuser")
        position.is_highlighted = True
        position.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from highlighted positions
        '''
        position, _ = AvailablePositionDesignation.objects.get_or_create(cp_id=pk)
        in_group_or_403(self.request.user, "superuser")
        position.is_highlighted = False
        position.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BureauBiddersRankings(APIView):

    permission_classes = [Or(isDjangoGroupMember('ao_user'), isDjangoGroupMember('bureau_user'), isDjangoGroupMember('post_user')), ]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, type=openapi.TYPE_STRING, description='perdet of Bureau bidder'),
            openapi.Parameter('cp_id', openapi.IN_PATH, type=openapi.TYPE_STRING, description='cp_id of position')
        ])

    def get(self, request, pk, cp_id):
        """
        Return position information for all of bidders' bids including their ranking information for those positions
        """
        user_bids = bidservices.user_bids(pk, request.META['HTTP_JWT'])
        user_rankings = AvailablePositionRanking.objects.filter(bidder_perdet=pk).exclude(cp_id=cp_id)
        num_sl_bids = 0
        filtered_bids = []

        for bid in user_bids:
          try:
            pos_id = str(int(pydash.get(bid, 'position_info.id')))
            rank = user_rankings.filter(cp_id=pos_id).values_list("rank", flat=True).first()
            if rank is not None:
                num_sl_bids += 1
                hasBureauPermissions = empservices.has_bureau_permissions(pos_id, self.request.META['HTTP_JWT'])
                hasOrgPermissions = empservices.has_org_permissions(pos_id, self.request.META['HTTP_JWT'])
                if hasOrgPermissions or hasBureauPermissions:
                    bid["ranking"] = rank
                    filtered_bids.append(bid)
          except Exception as e:
            logger.error(f"{type(e).__name__} at line {e.__traceback__.tb_lineno} of {__file__}: {e}")

        filtered_bids.sort(key=lambda x: x['ranking'])
        other_sl_bids = num_sl_bids - len(filtered_bids)
        return Response({
            "results": filtered_bids,
            "other-sl-bidcount": 0 if pydash.is_negative(other_sl_bids) else other_sl_bids,
        })
