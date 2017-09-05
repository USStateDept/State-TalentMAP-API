from django.conf.urls import url

from talentmap_api.language import views
from talentmap_api.common.urls import get_retrieve, get_list

urlpatterns = [
    url(r'^$', views.LanguageQualificationListView.as_view({**get_list, "put": "create"}), name='language.Qualification-list-create'),
    url(r'^(?P<pk>[0-9]+)/$', views.LanguageQualificationListView.as_view(get_retrieve), name='language.Qualification-detail'),
]
