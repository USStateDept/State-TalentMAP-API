from django.conf.urls import url

from talentmap_api.bidding.views import waiver as views
from talentmap_api.common.urls import get_retrieve, get_list, patch_update, post_create

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.WaiverClientView.as_view({**get_retrieve, **patch_update}), name='bidding.Waiver-detail'),
    url(r'^$', views.WaiverClientView.as_view({**get_list, **post_create}), name='bidding.Waiver-list-create'),
]
