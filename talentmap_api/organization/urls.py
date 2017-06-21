from django.conf.urls import url

from talentmap_api.organization import views

get_list = {'get': 'list'}

urlpatterns = [
    url(r'^$', views.OrganizationListView.as_view(get_list), name='view-organizations'),
]
