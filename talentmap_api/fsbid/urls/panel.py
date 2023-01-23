from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import panel as views
from talentmap_api.fsbid.views import agenda as agenda_views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^categories/$', views.PanelCategoriesView.as_view(), name='panel-FSBid-categories'),
    url(r'^dates/$', views.PanelDatesView.as_view(), name='panel-FSBid-dates'),
    url(r'^statuses/$', views.PanelStatusesView.as_view(), name='panel-FSBid-statuses'),
    url(r'^types/$', views.PanelTypesView.as_view(), name='panel-FSBid-types'),
    url(r'^meetings/', views.PanelMeetingsView.as_view(), name="panel-meetings-list"),
    url(r'^(?P<pk>[0-9]+)/agendas/', agenda_views.PanelAgendasListView.as_view(), name="panel-agendas-list"),
]

urlpatterns += router.urls
