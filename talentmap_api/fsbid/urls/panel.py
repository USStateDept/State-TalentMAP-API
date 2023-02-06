from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import panel as views
from talentmap_api.fsbid.views import agenda as agenda_views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^reference/categories/$', views.PanelCategoriesView.as_view(), name='panel-FSBid-reference-categories'),
    url(r'^reference/dates/$', views.PanelDatesView.as_view(), name='panel-FSBid-reference-dates'),
    url(r'^reference/statuses/$', views.PanelStatusesView.as_view(), name='panel-FSBid-reference-statuses'),
    url(r'^reference/types/$', views.PanelTypesView.as_view(), name='panel-FSBid-reference-types'),
    url(r'^meetings/', views.PanelMeetingsView.as_view(), name="panel-meetings-list"),
    url(r'^(?P<pk>[0-9]+)/agendas/', agenda_views.PanelAgendasListView.as_view(), name="panel-agendas-list"),
]

urlpatterns += router.urls
