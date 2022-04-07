from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import employee as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^perdet_seq_num/$', views.FSBidEmployeePerdetSeqNumActionView.as_view(), name='employee.FSBid-perdet_seq_num-actions'),
    url(r'^bureau_permissions/$', views.FSBidBureauUserPermissionsView.as_view(), name='employee.FSBid-bureau-permission'),
    url(r'^org_permissions/$', views.FSBidOrgUserPermissionsView.as_view(), name='employee.FSBid-org-permission'),
    url(r'^separations/(?P<pk>[0-9]+)/$', views.FSBidSeparationsView.as_view(), name='employee.FSBid-separations'),
    url(r'^assignments_separations_bids/(?P<pk>[0-9]+)/$', views.FSBidAssignmentSeparationsBidsView.as_view(), name='employee.FSBid-assignments,separations,bids'),
]
urlpatterns += router.urls
