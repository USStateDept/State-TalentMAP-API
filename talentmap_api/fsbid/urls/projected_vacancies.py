from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import projected_vacancies as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^export/$', views.FSBidProjectedVacanciesCSVView.as_view(), name="projected-vacancies-FSBid-projected-vacancies-csv"),
    url(r'^(?P<pk>[0-9]+)/$', views.FSBidProjectedVacancyView.as_view(), name='projected-vacancies-FSBid-projected-vacancy'),
    url(r'^tandem/$', views.FSBidProjectedVacanciesTandemListView.as_view(), name="projected-vacancies-FSBid-projected-vacancies-actions"),
    url(r'^tandem/export/$', views.FSBidProjectedVacanciesTandemCSVView.as_view(), name="projected-vacancies-FSBid-projected-vacancies-actions"),
    url(r'^$', views.FSBidProjectedVacanciesListView.as_view(), name="projected-vacancies-FSBid-projected-vacancies-actions"),
]

urlpatterns += router.urls
