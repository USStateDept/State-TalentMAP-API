from django.conf.urls import url

from talentmap_api.integrations import views as views

from rest_framework import routers

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^run/(?P<pk>[0-9]+)/$', views.DataSyncActionView.as_view(), name="integrations.DataSyncActionView"),
    url(r'^updatestringrepresentations/$', views.UpdateStringRepresentationsActionView.as_view(), name="integrations.UpdateStringRepresentationsActionView"),
    url(r'^updaterelationships/$', views.UpdateRelationshipsActionView.as_view(), name="integrations.UpdateRelationshipsActionView"),
    url(r'', views.DataSyncListView.as_view(), name="integrations.DataSyncListView"),
]

urlpatterns += router.urls