from django.conf.urls import url
from rest_framework import routers

from talentmap_api.available_positions.views import available_position as views

from talentmap_api.common.urls import get_list

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/$', views.AvailablePositionFavoriteListView.as_view(), name='view-favorite-available-positions'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.AvailablePositionFavoriteActionView.as_view(), name='available_positions-AvailablePositionFavorite-favorite'),
]

urlpatterns += router.urls
