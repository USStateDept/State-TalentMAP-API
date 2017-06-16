from django.conf.urls import url

from talentmap_api.language import views

get_list = {'get': 'list'}

urlpatterns = [
    url(r'^$', views.LanguageListView.as_view(get_list), name='view-languages'),
    url(r'^proficiencies/$', views.LanguageProficiencyListView.as_view(get_list), name='view-language-proficiencies'),
    url(r'^qualifications/$', views.LanguageQualificationListView.as_view(get_list), name='view-language-qualifications')
]
