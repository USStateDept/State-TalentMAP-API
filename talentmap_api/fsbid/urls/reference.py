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
]

urlpatterns += router.urls
