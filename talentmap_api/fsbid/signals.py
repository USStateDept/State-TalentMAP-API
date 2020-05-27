from django.conf import settings
from django.dispatch import Signal, receiver
from talentmap_api.projected_vacancies.models import ProjectedVacancyFavorite
from talentmap_api.available_positions.models import AvailablePositionFavorite
import talentmap_api.fsbid.services.projected_vacancies as pv_services
import talentmap_api.fsbid.services.available_positions as ap_services
import logging

logger = logging.getLogger(__name__)

FAVORITES_LIMIT = settings.FAVORITES_LIMIT

ap_favorites_signal = Signal(providing_args=["user", "request"])
pv_favorites_signal = Signal(providing_args=["user", "request"])

@receiver(get_ap_favorites)
def archive_ap_favorites(sender, **kwargs):
    user = kwargs.get('user')
    request = kwargs.get('request')
    favs = AvailablePositionFavorite.objects.filter(user=user, archived=False).values_list("cp_id", flat=True)
    if len(favs) >= FAVORITES_LIMIT:
        # Pos nums is string to pass correctly to services url
        pos_nums = ','.join(favs)
        # List favs is list of integers instead of strings for comparison
        list_favs = list(map(lambda x: int(x), favs))
        # Valid resulting ids from fsbid
        returned_ids = ap_services.get_ap_favorite_ids(QueryDict(f"id={pos_nums}&limit=999999&page=1"), request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        # Need to determine which ids need to be archived using comparison of lists above
        outdated_ids = []
        for fav_id in list_favs:
            if fav_id not in returned_ids:
                outdated_ids.append(fav_id)
        if len(outdated_ids) > 0:
            AvailablePositionFavorite.objects.filter(cp_id__in=outdated_ids).update(archived=True)
            print("Available Position favorites archived")
        else:
            print("No favorites were archived")
    

@receiver(get_pv_favorites)
def archive_pv_favorites(sender, **kwargs):
    user = kwargs.get('user')
    request = kwargs.get('request')
    favs = ProjectedVacancyFavorite.objects.filter(user=user, archived=False).values_list("fv_seq_num", flat=True)
    if len(favs) >= FAVORITES_LIMIT:
        # Pos nums is string to pass correctly to services url
        pos_nums = ','.join(favs)
        # List favs is list of integers instead of strings for comparison
        list_favs = list(map(lambda x: int(x), favs))
        # Valid resulting ids from fsbid
        returned_ids = pv_services.get_pv_favorite_ids(QueryDict(f"id={pos_nums}&limit=999999&page=1"), request.META['HTTP_JWT'], f"{request.scheme}://{request.get_host()}")
        # Need to determine which ids need to be archived using comparison of lists above
        outdated_ids = []
        for fav_id in list_favs:
            if fav_id not in returned_ids:
                outdated_ids.append(fav_id)
        if len(outdated_ids) > 0:
            ProjectedVacancyFavorite.objects.filter(fv_seq_num__in=outdated_ids).update(archived=True)
            print("Projected Vacancy favorites were archived")
        else:
            print("No favorites were archived")
    