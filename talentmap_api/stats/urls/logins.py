from django.conf.urls import url

from talentmap_api.common.urls import get_list
from talentmap_api.stats import views

urlpatterns = [
    # login stats
    url(r'^login/$', views.UserLoginActionView.as_view({'post': 'submit'}), name='stats.UserLogin-actions-submit'),
    url(r'^logins/$', views.UserLoginListView.as_view({**get_list}), name='stats.UserLoginList'),
    url(r'^distinctlogins/$', views.UserLoginDistinctListView.as_view({**get_list}), name='stats.UserLoginDistinctList'),

    # position view stats
    url(r'^positionview/$', views.ViewPositionActionView.as_view({'post': 'submit'}), name='stats.ViewPosition-actions-submit'),
    url(r'^positionviews/$', views.ViewPositionListView.as_view({**get_list}), name='stats.ViewPositionList'),
    url(r'^distinctpositionviews/$', views.ViewPositionDistinctListView.as_view({**get_list}), name='stats.ViewPositionDistinctList'),

    # system resources
    url(r'^sysmon/', views.SystemResources.as_view({'get': 'get'}), name='stats.SystemResources'),
]
