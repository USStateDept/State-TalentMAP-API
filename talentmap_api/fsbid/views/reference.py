from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.reference as services

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
        return Response(services.get_dangerpay(request.META['HTTP_JWT']))

class FSBidCyclesView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the cycles
        '''
        return Response(services.get_cycles(request.META['HTTP_JWT']))

class FSBidBureausView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the bureaus
        '''
        return Response(services.get_bureaus(request.META['HTTP_JWT']))

class FSBidDifferentialRatesView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the differential rates
        '''
        return Response(services.get_differential_rates(request.META['HTTP_JWT']))

class FSBidGradesView(BaseView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the grades
        '''
        return Response(services.get_grade(request.META['HTTP_JWT']))

class FSBidLanguagesView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the languages
        '''
        return Response(services.get_languages(request.META['HTTP_JWT']))

class FSBidTourOfDutiesView(BaseView):

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        '''
        Gets the tour of duties
        '''
        return Response(services.get_tour_of_duties(request.META['HTTP_JWT']))
        #return Response(services.get_fsbid_results("tourofduties", request.META['HTTP_JWT'], fsbid_tour_of_duties_to_talentmap_tour_of_duties))