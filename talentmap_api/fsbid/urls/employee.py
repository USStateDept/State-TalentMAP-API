from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import employee as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^perdet_seq_num/$', views.FSBidEmployeePerdetSeqNumActionView.as_view(), name='employee.FSBid-perdet_seq_num-actions'),
    url(r'^bureau_permissions/$', views.FSBidBureauUserPermissionsView.as_view(), name='employee.FSBid-bureau-permission'),
    url(r'^org_permissions/$', views.FSBidOrgUserPermissionsView.as_view(), name='employee.FSBid-org-permission'),
    url(r'^separations/$', views.FSBidSeparationsView.as_view(), name='employee.FSBid-separations'),
    # url(r'^separations/(?P<pk>[0-9]+)/$', views.FSBidOrgUserPermissionsView.as_view(), name='employee.FSBid-separations'), if we instead want the perdet in the url for TM - less flexible
]
urlpatterns += router.urls
