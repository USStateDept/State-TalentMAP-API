from django.conf.urls import url
from rest_framework import routers

from talentmap_api.available_positions.views import available_position as views

from talentmap_api.common.urls import patch_update

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/export/$', views.FavoritesCSVView.as_view(), name='export-all-favorites'),
    url(r'^favorites/$', views.AvailablePositionFavoriteListView.as_view(), name='view-favorite-available-positions'),
    url(r'^favorites/ids/$', views.AvailablePositionFavoriteIdsListView.as_view(), name='view-favorite-available-positions-ids'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.AvailablePositionFavoriteActionView.as_view(), name='available_positions-AvailablePositionFavorite-favorite'),
    url(r'^(?P<pk>[0-9]+)/designation/$', views.AvailablePositionDesignationView.as_view({**patch_update}), name='available_positions-AvailablePositionDesignation-designation'),
    url(r'^highlight/$', views.AvailablePositionHighlightListView.as_view(), name='view-highlighted-availablepositions'),
    url(r'^(?P<pk>[0-9]+)/highlight/$', views.AvailablePositionHighlightActionView.as_view(), name='available_positions-AvailablePositionDesignation-highlight'),
]

urlpatterns += router.urls
