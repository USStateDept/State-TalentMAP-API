from django.conf.urls import url

from talentmap_api.common.urls import patch_update, get_retrieve, get_list, post_create
from talentmap_api.bidding.views import survey as views

urlpatterns = [
    url(r'^$', views.StatusSurveyView.as_view({**get_list, **post_create}), name='bidding.StatusSurvey-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.StatusSurveyView.as_view({**patch_update, **get_retrieve}), name='bidding.StatusSurvey-detail'),
]
