import logging

from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.reference as services

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


class FSBidClassificationsView(BaseView):
    uri = "bidderTrackingPrograms"
    mapping_function = services.fsbid_classifications_to_talentmap_classifications

    # BTP return some duplicated objects with unique bid season references
    # This nests those unique values in an array under one object to aggregate the duplicated data
    # As of 03/21, the only applicable edge cases are `Tenured 4` and `Differential Bidder`
    def modClassifications(self, results):
        duplicate_results = list(results)
        unique_codes = set(map(lambda x: x['code'], duplicate_results))

        nested_results, seasons, classification_text, glossary_term = [], [], '', ''
        for code in unique_codes:
            for classification in duplicate_results:
                if classification['code'] == code:
                    classification_text = classification['text']
                    glossary_term = classification['glossary_term']
                    season_txt = classification['season_text'].split(' - ')
                    seasons.append({
                        'id': classification['id'],
                        'season_text': season_txt[1] if len(season_txt) > 1 else None
                    })

            nested_results.append({
                'code': code,
                'text': classification_text,
                'seasons': seasons,
                'glossary_term': glossary_term
            })
            seasons, classification_text = [], ''
        return nested_results

    mod_function = modClassifications

class FSBidPostIndicatorsView(BaseView):
    uri = "references/postAttributes?codeTableName=PostIndicatorTable"
    mapping_function = services.fsbid_post_indicators_to_talentmap_indicators


class FSBidUnaccompaniedStatusView(BaseView):
    uri = "references/postAttributes?codeTableName=UnaccompaniedTable"
    mapping_function = services.fsbid_us_to_talentmap_us


class FSBidCommuterPostsView(BaseView):
    uri = "references/postAttributes?codeTableName=CommuterPostTable"
    mapping_function = services.fsbid_commuter_posts_to_talentmap_commuter_posts
