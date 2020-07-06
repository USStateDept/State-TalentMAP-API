from django.conf.urls import url

from talentmap_api.feedback.views import feedback as views
from talentmap_api.common.urls import get_retrieve, get_list, post_create, delete_destroy

urlpatterns = [
    url(r'^$', views.FeedbackUserView.as_view({**post_create, **get_list}), name='feedback.FeedbackEntry-create'),
    url(r'^all/(?P<pk>[0-9]+)/$', views.FeedbackAdminView.as_view({**get_retrieve, **delete_destroy}), name='feedback.FeedbackEntry-detail'),
    url(r'^all/$', views.FeedbackAdminView.as_view({**get_list}), name='feedback.FeedbackEntry-list'),
]
