from django.conf.urls import url

from talentmap_api.organization import views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.OrganizationListView.as_view(get_list), name='view-organizations'),
    url(r'^(?P<pk>[0-9]+)/$', views.OrganizationListView.as_view(get_retrieve), name='view-organization-details'),

    url(r'^posts/$', views.PostListView.as_view(get_list), name='view-posts'),
    url(r'^posts/(?P<pk>[0-9]+)/$', views.PostListView.as_view(get_retrieve), name='view-post-details'),

    url(r'^tod/$', views.TourOfDutyListView.as_view(get_list), name='view-tods'),
    url(r'^tod/(?P<pk>[0-9]+)/$', views.TourOfDutyListView.as_view(get_retrieve), name='view-tod-details'),
]
