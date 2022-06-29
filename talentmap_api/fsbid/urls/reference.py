from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import reference as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^dangerpay/$', views.FSBidDangerPayView.as_view(), name='FSBid-danger-pay'),
    url(r'^cycles/$', views.FSBidCyclesView.as_view(), name='FSBid-cycles'),
    url(r'^bureaus/$', views.FSBidBureausView.as_view(), name='FSBid-bureaus'),
    url(r'^differentialrates/$', views.FSBidDifferentialRatesView.as_view(), name='FSBid-differential-rates'),
    url(r'^grades/$', views.FSBidGradesView.as_view(), name='FSBid-grades'),
    url(r'^languages/$', views.FSBidLanguagesView.as_view(), name='FSBid-languages'),
    url(r'^tourofduties/$', views.FSBidTourOfDutiesView.as_view(), name='FSBid-tour-of-duties'),
    url(r'^codes/$', views.FSBidCodesView.as_view(), name='FSBid-skill-codes'),
    url(r'^cones/$', views.FSBidConesView.as_view(), name='FSBid-cones'),
    url(r'^locations/$', views.FSBidLocationsView.as_view(), name='FSBid-locations'),
    url(r'^classifications/$', views.FSBidClassificationsView.as_view(), name='FSBid-classifications'),
    url(r'^postindicators/$', views.FSBidPostIndicatorsView.as_view(), name='FSBid-post-indicators'),
    url(r'^unaccompaniedstatuses/$', views.FSBidUnaccompaniedStatusView.as_view(), name='FSBid-unaccompanied-statuses'),
    url(r'^commuterposts/$', views.FSBidCommuterPostsView.as_view(), name='FSBid-commuter-posts'),
    url(r'^travelfunctions/$', views.FSBidTravelFunctionsView.as_view(), name='FSBid-travel-functions'),
]

urlpatterns += router.urls
