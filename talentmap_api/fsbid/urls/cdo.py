from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import cdo as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^position/(?P<pk>[0-9]+)/client/(?P<client_id>[0-9]+)/$', views.FSBidListPositionActionView.as_view(), name='cdo-bidding.FSBid-position-actions'),
    url(r'^position/(?P<pk>[0-9]+)/client/(?P<client_id>[0-9]+)/submit/$', views.FSBidListBidActionView.as_view(), name='cdo-bidding.FSBid-bid-actions'),
    url(r'^position/(?P<pk>[0-9]+)/client/(?P<client_id>[0-9]+)/register/$', views.FSBidListBidRegisterView.as_view(), name='cdo-bidding.FSBid-bid-actions-register'),
    url(r'^client/(?P<client_id>[0-9]+)/export/$', views.FSBidBidClientListCSVView.as_view(), name="cdo-bidding.FSBid-bid-actions"),
    url(r'^client/(?P<client_id>[0-9]+)/$', views.FSBidListView.as_view(), name="cdo-bidding-FSBid-bid-actions"),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidCDOView.as_view(), name='FSBid-cdo'),
    url(r'^$', views.FSBidCDOListView.as_view(), name='FSBid-cdo_list'),
    url(r'^classifications/(?P<client_id>[0-9]+)/$', views.FSBidClientEditClassifications.as_view(), name='cdo-client-classifications.FSBid-classifications'),
]

urlpatterns += router.urls
