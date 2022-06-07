from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import agenda_employees as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidAgendaEmployeesListView.as_view(), name="agenda-employees-FSBid-agenda-employees-list"),
    url(r'^export/$', views.FSBidAgendaEmployeesCSVView.as_view(), name="agenda-employees-FSBid-agenda-employees-export"),
    url(r'^reference/current-organizations/$', views.FSBidPersonCurrentOrganizationsView.as_view(), name='agenda-employees-fsbid-reference-current-organizations'),
    url(r'^reference/handshake-organizations/$', views.FSBidPersonHandshakeOrganizationsView.as_view(), name='agenda-employees-fsbid-reference-hs-organizations'),
    url(r'^reference/current-bureaus/$', views.FSBidPersonCurrentBureausView.as_view(), name='agenda-employees-fsbid-reference-current-bureaus'),
    url(r'^reference/handshake-bureaus/$', views.FSBidPersonHandshakeBureausView.as_view(), name='agenda-employees-fsbid-reference-hs-bureaus'),
]

urlpatterns += router.urls
