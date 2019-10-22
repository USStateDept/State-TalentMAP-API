from django.conf.urls import url
from rest_framework import routers

from talentmap_api.common.urls import patch_update
from talentmap_api.fsbid.views import employee as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^perdet_seq_num/$', views.FSBidEmployeePerdetSeqNumActionView.as_view(), name='employee.FSBid-perdet_seq_num-actions'),
]
urlpatterns += router.urls
