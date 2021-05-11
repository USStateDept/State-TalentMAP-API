from django.conf.urls import url
from rest_framework import routers

from talentmap_api.available_positions.views import available_position as views

from talentmap_api.common.urls import get_retrieve, get_list, patch_update, post_create

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/export/$', views.FavoritesCSVView.as_view(), name='export-all-favorites'),
    url(r'^favorites/$', views.AvailablePositionFavoriteListView.as_view(), name='view-favorite-available-positions'),
    url(r'^favorites/ids/$', views.AvailablePositionFavoriteIdsListView.as_view(), name='view-favorite-available-positions-ids'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.AvailablePositionFavoriteActionView.as_view(), name='available_positions-AvailablePositionFavorite-favorite'),
    url(r'^(?P<pk>[0-9]+)/designation/$', views.AvailablePositionDesignationView.as_view({**patch_update}), name='available_positions-AvailablePositionDesignation-designation'),
    url(r'^highlight/$', views.AvailablePositionHighlightListView.as_view(), name='view-highlighted-availablepositions'),
    url(r'^(?P<pk>[0-9]+)/highlight/$', views.AvailablePositionHighlightActionView.as_view(), name='available_positions-AvailablePositionDesignation-highlight'),
    # Rankings
    url(r'^ranking/$', views.AvailablePositionRankingView.as_view({**get_list, **post_create}), name='view-ranking-available-positions'),
    url(r'^rankings/(?P<pk>[0-9]+)/(?P<cp_id>[0-9]+)/$', views.BureauBiddersRankings.as_view(), name='bureau-bidder-rankings'),
    url(r'^(?P<pk>[0-9]+)/ranking/$', views.AvailablePositionRankingView.as_view({'delete': 'perform_delete'}), name='delete-ranking-available-positions'),
    url(r'^(?P<pk>[0-9]+)/ranking/lock/$', views.AvailablePositionRankingLockView.as_view({'get': 'get', 'put': 'put', 'delete': 'delete'}), name='view-ranking-available-positions-lock'),
]

urlpatterns += router.urls
