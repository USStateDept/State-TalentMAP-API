import logging
import coreapi

from django.http import QueryDict

from django.conf import settings

from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, mixins

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from talentmap_api.available_tandem.models import AvailableFavoriteTandem
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.projected_tandem.models import ProjectedFavoriteTandem

import talentmap_api.fsbid.services.available_positions as services
import talentmap_api.fsbid.services.projected_vacancies as pvservices
import talentmap_api.fsbid.services.common as comservices

logger = logging.getLogger(__name__)

FAVORITES_LIMIT = settings.FAVORITES_LIMIT


class AvailableFilter():
    declared_filters = [
        "exclude_available",
        "exclude_projected",
    ]

    use_api = True

    class Meta:
        fields = "__all__"


class AvailableFavoriteTandemListView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='A page number within the paginated result set.'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of results to return per page.'),
            openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Ordering')
        ])

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the user's tandem favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailableFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        limit = request.query_params.get('limit', 15)
        page = request.query_params.get('page', 1)
        ordering = request.query_params.get('ordering', None)
        if aps:
            comservices.archive_favorites(aps, request)
            pos_nums = ','.join(aps)
            return Response(services.get_available_positions(
                QueryDict(f"id={pos_nums}&limit={limit}&page={page}&ordering={ordering}"),
                request.META['HTTP_JWT'],
                f"{request.scheme}://{request.get_host()}"))
        return Response({"count": 0, "next": None, "previous": None, "results": []})


class AvailableFavoriteTandemIdsListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of the ids of the user's favorite available positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailableFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        return Response(aps)


class FavoritesTandemCSVView(APIView):

    permission_classes = (IsAuthenticated,)
    filter_class = AvailableFilter

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('exclude_available', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Whether to exclude available positions'),
            openapi.Parameter('exclude_projected', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Whether to exclude projected vacancies'),
        ])

    def get(self, request, *args, **kwargs):
        """
        Return a list of all of the user's favorite positions.
        """
        user = UserProfile.objects.get(user=self.request.user)
        data = []
        # AP Tandem
        aps = AvailableFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        if request.query_params.get('exclude_available') != 'true' and aps:
            pos_nums = ','.join(aps)
            apdata = services.get_available_positions(
                QueryDict(f"id={pos_nums}&limit={len(aps)}&page=1"),
                request.META['HTTP_JWT'],
                f"{request.scheme}://{request.get_host()}")
            data = data + apdata.get('results')
        # PV Tandem
        pvs = ProjectedFavoriteTandem.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
        if request.query_params.get('exclude_projected') != 'true' and pvs:
            pv_pos_nums = ','.join(pvs)
            pvdata = pvservices.get_projected_vacancies(
                QueryDict(f"id={pv_pos_nums}&limit={len(pvs)}&page=1"),
                request.META['HTTP_JWT'],
                f"{request.scheme}://{request.get_host()}")
            data = data + pvdata.get('results')
        return comservices.get_ap_and_pv_csv(data, "tandem-favorites", True)


class AvailableFavoriteTandemActionView(APIView):
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
        if AvailableFavoriteTandem.objects.filter(user=user, cp_id=pk, archived=False).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the available position as a favorite
        '''
        user = UserProfile.objects.get(user=self.request.user)
        aps = AvailableFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        comservices.archive_favorites(aps, request)
        aps_after_archive = AvailableFavoriteTandem.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
        if len(aps_after_archive) >= FAVORITES_LIMIT:
            return Response({"limit": FAVORITES_LIMIT}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        else:
            AvailableFavoriteTandem.objects.get_or_create(user=user, cp_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the available position from favorites
        '''
        user = UserProfile.objects.get(user=self.request.user)
        AvailableFavoriteTandem.objects.filter(user=user, cp_id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
