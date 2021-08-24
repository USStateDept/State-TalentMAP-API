from django.conf.urls import url

from talentmap_api.glossary.views import glossary as views
from talentmap_api.common.urls import get_retrieve, get_list, patch_update, post_create

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.GlossaryView.as_view({**get_retrieve, **patch_update}), name='glossary.GlossaryEntry-detail'),
    url(r'^$', views.GlossaryView.as_view({**get_list, **post_create}), name='glossary.GlossaryEntry-list-create'),
    url(r'^export/$', views.GlossaryCSVView.as_view(), name='glossary.Glossary-export'),
]
