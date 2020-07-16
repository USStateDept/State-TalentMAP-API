from django.conf.urls import url
from rest_framework import routers

from talentmap_api.available_tandem.views import available_tandem as views

from talentmap_api.common.urls import patch_update

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/export/$', views.FavoritesTandemCSVView.as_view(), name='export-all-tandem-favorites'),
    url(r'^favorites/$', views.AvailableFavoriteTandemListView.as_view(), name='view-favorite-tandem'),
    url(r'^favorites/ids/$', views.AvailableFavoriteTandemIdsListView.as_view(), name='view-favorite-tandem-ids'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.AvailableFavoriteTandemActionView.as_view(), name='available_tandemFavorite-favorite'),
]

urlpatterns += router.urls
