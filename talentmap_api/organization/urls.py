from django.conf.urls import url

from talentmap_api.organization import views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.OrganizationListView.as_view(get_list), name='view-organizations'),
    url(r'^(?P<pk>[0-9]+)/$', views.OrganizationListView.as_view(get_retrieve), name='view-organization-details'),

    url(r'^locations/$', views.LocationListView.as_view(get_list), name='view-locations'),
    url(r'^locations/(?P<pk>[0-9]+)/$', views.LocationListView.as_view(get_retrieve), name='view-location-details'),

    url(r'^tod/$', views.TourOfDutyListView.as_view(get_list), name='view-tods'),
    url(r'^tod/(?P<pk>[0-9]+)/$', views.TourOfDutyListView.as_view(get_retrieve), name='view-tod-details'),
]
