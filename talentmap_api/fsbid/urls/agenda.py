from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import agenda as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^agenda_items/$', views.AgendaItemListView.as_view(), name="agenda-agenda-items"),
    url(r'^agenda_items/(?P<pk>[0-9]+)/$', views.AgendaItemView.as_view(), name="agenda-agenda-items"),
    url(r'^agenda_items/export/$', views.AgendaItemCSVView.as_view(), name="agenda-export-agenda-items"),
    url(r'^remarks/$', views.AgendaRemarksView.as_view(), name="agenda-reference-remarks"),
    url(r'^remark-categories/$', views.AgendaRemarkCategoriesView.as_view(), name="agenda-reference-remarkss-categories"),
    url(r'^statuses/$', views.AgendaStatusesView.as_view(), name="agenda-reference-statuses"),
]

urlpatterns += router.urls
