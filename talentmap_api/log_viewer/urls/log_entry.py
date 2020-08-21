from django.conf.urls import url

from rest_framework import routers

from talentmap_api.log_viewer.views import log_entry as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<string>[\w\-\.]+)/$', views.LogEntryView.as_view(), name="log_viewer.LogEntry"),
    url(r'', views.LogEntryListView.as_view(), name="log_viewer.LogEntryList"),
]

urlpatterns += router.urls
