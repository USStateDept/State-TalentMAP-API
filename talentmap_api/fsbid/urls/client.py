from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import client as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/suggestions/$', views.FSBidClientSuggestionsView.as_view(), name='FSBid-client-suggestions'),
    url(r'^export/$', views.FSBidClientCSVView.as_view(), name="FSBid-client_export"),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidClientView.as_view(), name='FSBid-client'),
    url(r'^$', views.FSBidClientListView.as_view(), name='FSBid-client_list'),
]

urlpatterns += router.urls
