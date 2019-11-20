from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.reference as services
import talentmap_api.fsbid.services.common as common

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from itertools import groupby
from operator import itemgetter

import logging
logger = logging.getLogger(__name__)

class FSBidDangerPayView(BaseView):
    uri = "dangerpays"
    mapping_function = services.fsbid_danger_pay_to_talentmap_danger_pay

class FSBidCyclesView(BaseView):
    uri = "cycles"
    mapping_function = services.fsbid_cycles_to_talentmap_cycles

class FSBidBureausView(BaseView):
    uri = "bureaus"
    mapping_function = services.fsbid_bureaus_to_talentmap_bureaus

class FSBidDifferentialRatesView(BaseView):
    uri = "differentialrates"
    mapping_function = services.fsbid_differential_rates_to_talentmap_differential_rates

class FSBidGradesView(BaseView):
    uri = "grades"
    mapping_function = services.fsbid_grade_to_talentmap_grade

class FSBidLanguagesView(BaseView):
    uri = "languages"
    mapping_function = services.fsbid_languages_to_talentmap_languages

class FSBidTourOfDutiesView(BaseView):
    uri = "tourofduties"
    mapping_function = services.fsbid_tour_of_duties_to_talentmap_tour_of_duties

class FSBidCodesView(BaseView):
    uri = "skillCodes"
    mapping_function = services.fsbid_codes_to_talentmap_codes

class FSBidLocationsView(BaseView):
    uri = "locations"
    mapping_function = services.fsbid_locations_to_talentmap_locations

class FSBidConesView(BaseView):
    uri = "skillCodes"
    mapping_function = services.fsbid_codes_to_talentmap_cones

    def modCones(self, results):
        results = list(results)
        values = set(map(lambda x: x['category'], results))

        newlist, codes = [], []
        for cone in values:
            for info in results:
                if info['category'] == cone:
                    codes.append({'code': info['code'], 'id': info['id'], 'description': info['description']})

            newlist.append({'category': cone, 'skills': codes})
            codes = []
        return newlist

    mod_function = modCones
