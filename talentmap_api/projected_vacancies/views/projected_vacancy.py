from django.shortcuts import render
from django.http import QueryDict

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite

from talentmap_api.user_profile.models import UserProfile

import talentmap_api.fsbid.services as services


class ProjectedVacancyFavoriteListView(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """
        get:
        Return a list of all of the user's favorite projected vacancies.
        """
        user = UserProfile.objects.get(user=self.request.user)
        pvs = ProjectedVacancyFavorite.objects.filter(user=user).values_list("fv_seq_number", flat=True)
        if len(pvs) > 0:
            pos_nums = ','.join(pvs)
            return Response(services.get_projected_vacancies(QueryDict(f"id={pos_nums}")))
        else:
            return Response({"count": 0, "next": None, "previous": None, "results": []})


class ProjectedVacancyFavoriteActionView(APIView):
    '''
    Controls the favorite status of a projected vacancy

    Responses adapted from Github gist 'stars' https://developer.github.com/v3/gists/#star-a-gist
    '''

    permission_classes = (IsAuthenticated,)

    def get(self, request, pk, format=None):
        '''
        Indicates if the projected vacancy is a favorite

        Returns 204 if the projected vacancy is a favorite, otherwise, 404
        '''
        user = UserProfile.objects.get(user=self.request.user)
        if ProjectedVacancyFavorite.objects.filter(user=user, fv_seq_number=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Marks the projected vacancy as a favorite
        '''
        user = UserProfile.objects.get(user=self.request.user)
        pvf = ProjectedVacancyFavorite(user=user, fv_seq_number=pk)
        pvf.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the projected vacancy from favorites
        '''
        user = UserProfile.objects.get(user=self.request.user)
        ProjectedVacancyFavorite.objects.get(user=user, fv_seq_number=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
