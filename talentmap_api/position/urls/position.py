from rest_framework import routers
from django.conf.urls import url

from talentmap_api.position import views
from talentmap_api.common.urls import get_list

router = routers.SimpleRouter()
router.register(r'', views.PositionListView, base_name="position.Position")

urlpatterns = [
    url(r'^highlighted/$', views.PositionHighlightListView.as_view(get_list), name='view-highlighted-positions'),
    url(r'^favorites/$', views.PositionFavoriteListView.as_view(get_list), name='view-favorite-positions'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.PositionFavoriteActionView.as_view(), name='position.Position-favorite'),
    url(r'^(?P<pk>[0-9]+)/highlight/$', views.PositionHighlightActionView.as_view(), name='position.Position-highlight'),
]

urlpatterns += router.urls
