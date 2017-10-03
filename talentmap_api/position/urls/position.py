from django.conf.urls import url
from rest_framework import routers

from talentmap_api.position import views
from talentmap_api.common.urls import get_list, get_retrieve, patch_update

router = routers.SimpleRouter()
router.register(r'^classification', views.ClassificationListView, base_name="position.Classification")

urlpatterns = [
    url(r'^$', views.PositionListView.as_view(get_list), name='position.Position-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.PositionListView.as_view({**get_retrieve, **patch_update}), name='position.Position-detail'),
    url(r'^highlighted/$', views.PositionHighlightListView.as_view(get_list), name='view-highlighted-positions'),
    url(r'^favorites/$', views.PositionFavoriteListView.as_view(get_list), name='view-favorite-positions'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.PositionFavoriteActionView.as_view(), name='position.Position-favorite'),
    url(r'^(?P<pk>[0-9]+)/highlight/$', views.PositionHighlightActionView.as_view(), name='position.Position-highlight'),
]

urlpatterns += router.urls
