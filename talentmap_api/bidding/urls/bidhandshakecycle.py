from django.conf.urls import url
from rest_framework import routers

from talentmap_api.bidding.views import bidhandshakecycle as views
from talentmap_api.common.urls import get_retrieve, get_list, patch_update, post_create, delete_destroy

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.BidHandshakeCycleView.as_view({**get_retrieve, **patch_update, **delete_destroy}), name='bidding.BidHandshakeCycle-detail'),
    url(r'^$', views.BidHandshakeCycleView.as_view({**get_list, **post_create}), name='bidding.BidHandshakeCycle-list-create'),
]


urlpatterns += router.urls
