from django.conf.urls import url
from rest_framework import routers

from talentmap_api.position.views import position as views
from talentmap_api.common.urls import get_list, get_retrieve, patch_update

router = routers.SimpleRouter()
router.register(r'^classification', views.ClassificationListView, base_name="position.Classification")

urlpatterns = [
    url(r'^$', views.PositionListView.as_view(get_list), name='position.Position-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.PositionListView.as_view({**get_retrieve, **patch_update}), name='position.Position-detail'),
    url(r'^highlighted/$', views.PositionHighlightListView.as_view(get_list), name='view-highlighted-positions'),
    url(r'^(?P<pk>[0-9]+)/highlight/$', views.PositionHighlightActionView.as_view(), name='position.Position-highlight'),
    url(r'^(?P<pk>[0-9]+)/similar/$', views.PositionSimilarView.as_view(get_list), name='position.Position-similar'),
    url(r'^(?P<pk>[0-9]+)/waivers/$', views.PositionWaiverListView.as_view(get_list), name='position.Position-waivers'),
    url(r'^(?P<pk>[0-9]+)/waivers/(?P<waiver_pk>[0-9]+)/approve/$', views.PositionWaiverActionView.as_view({'get': 'approve'}), name='position.Position-waivers'),
    url(r'^(?P<pk>[0-9]+)/waivers/(?P<waiver_pk>[0-9]+)/deny/$', views.PositionWaiverActionView.as_view({'get': 'deny'}), name='position.Position-waivers')
]

urlpatterns += router.urls
