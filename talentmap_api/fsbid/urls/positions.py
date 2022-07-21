from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import positions as views

router = routers.SimpleRouter()

urlpatterns = [  
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidPositionView.as_view(), name='FSBid-generic-position'),
    url(r'^$', views.FSBidPositionListView.as_view(), name='FSBid-generic-positions'),
]

urlpatterns += router.urls
