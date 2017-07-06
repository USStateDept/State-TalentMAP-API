from django.conf.urls import url

from talentmap_api.language import views
from talentmap_api.common.urls import get_list, get_retrieve

urlpatterns = [
    url(r'^$', views.LanguageListView.as_view(get_list), name='view-languages'),
    url(r'^(?P<pk>[0-9]+)/$', views.LanguageListView.as_view(get_retrieve), name='view-language-details'),

    url(r'^proficiencies/$', views.LanguageProficiencyListView.as_view(get_list), name='view-language-proficiencies'),
    url(r'^proficiencies/(?P<pk>[0-9]+)/$', views.LanguageProficiencyListView.as_view(get_retrieve), name='view-language-proficiency-details'),

    url(r'^qualifications/$', views.LanguageQualificationListView.as_view(get_list), name='view-language-qualifications'),
    url(r'^qualifications/(?P<pk>[0-9]+)/$', views.LanguageQualificationListView.as_view(get_retrieve), name='view-language-qualification-details'),
]
