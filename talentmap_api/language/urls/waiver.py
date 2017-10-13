from django.conf.urls import url

from talentmap_api.common.urls import patch_update, get_retrieve, get_list, post_create
import talentmap_api.language.views as views

urlpatterns = [
    url(r'^$', views.WaiverView.as_view({**get_list, **post_create}), name='language.Waiver-list'),
    url(r'^(?P<pk>[0-9]+)/$', views.WaiverView.as_view({**patch_update, **get_retrieve}), name='language.Waiver-detail'),
]
