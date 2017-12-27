from django.conf.urls import url

from talentmap_api.user_profile.views import client as views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.CdoClientView.as_view(get_list), name='user_profile.UserProfile-client-list'),
    url(r'^statistics/$', views.CdoClientStatisticsView.as_view(), name='user_profile.UserProfile-client-statistics'),
    url(r'^(?P<pk>[0-9]+)/$', views.CdoClientView.as_view(get_retrieve), name='user_profile.UserProfile-client-detail'),
    url(r'^(?P<pk>[0-9]+)/survey/$', views.CdoClientSurveyView.as_view(get_list), name='bidding.StatusSurvey-client-list'),
    url(r'^(?P<pk>[0-9]+)/bids/$', views.CdoClientBidView.as_view(get_list), name='bidding.Bid-client-list'),
    url(r'^(?P<pk>[0-9]+)/bids/(?P<bid_id>[0-9]+)/prepanel/$', views.CdoClientBidView.as_view(get_retrieve), name='bidding.Bid-client-retrieve'),
    url(r'^(?P<pk>[0-9]+)/waivers/$', views.CdoClientWaiverView.as_view(get_list), name='bidding.Waiver-client-list'),
]
