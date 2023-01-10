from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import panel as views
from talentmap_api.fsbid.views import agenda as agenda_views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^dates/$', views.PanelDatesView.as_view(), name='panel-FSBid-dates'),
    url(r'^categories/$', views.PanelCategoriesView.as_view(), name='panel-FSBid-categories'),
    url(r'^(?P<pk>[0-9]+)/agendas', agenda_views.PanelAgendaListView.as_view(), name="panel-agenda-list"),
]

urlpatterns += router.urls
