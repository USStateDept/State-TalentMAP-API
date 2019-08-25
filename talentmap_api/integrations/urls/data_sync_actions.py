from django.conf.urls import url

from talentmap_api.integrations import views as views
from talentmap_api.common.urls import get_retrieve, get_list, patch_update, post_create

from rest_framework import routers

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^run/(?P<pk>[0-9]+)/$', views.DataSyncActionView.as_view(), name="integrations.DataSyncActionView"),
    url(r'^schedule/(?P<pk>[0-9]+)/$', views.DataSyncScheduleActionView.as_view({**patch_update}), name="integrations.DataSyncScheduleActionView"),
    url(r'^reset/(?P<pk>[0-9]+)/$', views.DataSyncScheduleResetView.as_view(), name="integrations.DataSyncScheduleActionView"),
    url(r'^updatestringrepresentations/$', views.UpdateStringRepresentationsActionView.as_view(), name="integrations.UpdateStringRepresentationsActionView"),
    url(r'^updaterelationships/$', views.UpdateRelationshipsActionView.as_view(), name="integrations.UpdateRelationshipsActionView"),
    url(r'^status/$', views.DataSyncTaskListView.as_view(get_list), name="integrations.SynchronizationTask-list-status"),
    url(r'', views.DataSyncListView.as_view(), name="integrations.DataSyncListView"),
]

urlpatterns += router.urls
