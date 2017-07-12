from django.conf.urls import url

from talentmap_api.position import views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.PositionListView.as_view(get_list), name='view-positions'),
    url(r'^(?P<pk>[0-9]+)/$', views.PositionListView.as_view(get_retrieve), name='view-position-details'),

    url(r'^grades/$', views.GradeListView.as_view(get_list), name='view-grades'),
    url(r'^grades/(?P<pk>[0-9]+)/$', views.GradeListView.as_view(get_retrieve), name='view-grade-details'),

    url(r'^skills/$', views.SkillListView.as_view(get_list), name='view-skills'),
    url(r'^skills/(?P<pk>[0-9]+)/$', views.SkillListView.as_view(get_retrieve), name='view-skill-details'),
]
