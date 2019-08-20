from django.conf.urls import url

from talentmap_api.common.urls import get_list
from talentmap_api.stats import views

urlpatterns = [
    url(r'^login/$', views.UserLoginActionView.as_view({'post': 'submit'}), name='stats.UserLogin-actions-submit'),
    url(r'^logins/$', views.UserLoginListView.as_view({**get_list}), name='stats.UserLoginList'),
    url(r'^distinctlogins/$', views.UserLoginDistinctListView.as_view({**get_list}), name='stats.UserLoginDistinctList')
]
