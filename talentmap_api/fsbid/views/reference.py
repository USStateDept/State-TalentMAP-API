from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.reference as services
import talentmap_api.fsbid.services.common as common

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

import logging
logger = logging.getLogger(__name__)

class FSBidDangerPayView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the danger pay
        '''
        return Response(common.get_fsbid_results("dangerpays", request.META['HTTP_JWT'], services.fsbid_danger_pay_to_talentmap_danger_pay))

class FSBidCyclesView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the cycles
        '''
        return Response(common.get_fsbid_results("cycles", request.META['HTTP_JWT'], services.fsbid_cycles_to_talentmap_cycles))

class FSBidBureausView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the bureaus
        '''
        return Response(common.get_fsbid_results("bureaus", request.META['HTTP_JWT'], services.fsbid_bureaus_to_talentmap_bureaus))

class FSBidDifferentialRatesView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the differential rates
        '''
        return Response(common.get_fsbid_results("differentialrates", request.META['HTTP_JWT'], services.fsbid_differential_rates_to_talentmap_differential_rates))


class FSBidGradesView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the grades
        '''
        return Response(common.get_fsbid_results("grades", request.META['HTTP_JWT'], services.fsbid_grade_to_talentmap_grade))


class FSBidLanguagesView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the languages
        '''
        return Response(common.get_fsbid_results("languages", request.META['HTTP_JWT'], services.fsbid_languages_to_talentmap_languages))


class FSBidTourOfDutiesView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the tour of duties
        '''
        return Response(common.get_fsbid_results("tourofduties", request.META['HTTP_JWT'], services.fsbid_tour_of_duties_to_talentmap_tour_of_duties))
