from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import agenda_employees as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^$', views.FSBidAgendaEmployeesListView.as_view(), name="eagenda-employees-FSBid-agenda-employees-list"),
]

urlpatterns += router.urls
