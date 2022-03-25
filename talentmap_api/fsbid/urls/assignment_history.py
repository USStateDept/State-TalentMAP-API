from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import assignment_history as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidAssignmentHistoryListView.as_view(), name="assignment-history-list"),
]

urlpatterns += router.urls
