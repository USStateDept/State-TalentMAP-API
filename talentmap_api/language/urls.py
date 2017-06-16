from django.conf.urls import url

from talentmap_api.language import views

urlpatterns = [
    url(r'^$', views.LanguageListView.as_view(), name='view-languages'),
    url(r'^proficiencies/$', views.LanguageProficiencyListView.as_view(), name='view-language-proficiencies'),
    url(r'^qualifications/$', views.LanguageQualificationListView.as_view(), name='view-language-qualifications')
]
