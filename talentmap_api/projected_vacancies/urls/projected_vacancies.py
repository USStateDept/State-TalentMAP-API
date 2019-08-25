from django.conf.urls import url
from rest_framework import routers

from talentmap_api.projected_vacancies.views import projected_vacancy as views

from talentmap_api.common.urls import get_list

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/$', views.ProjectedVacancyFavoriteListView.as_view(), name='view-favorite-projected-vacancies'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.ProjectedVacancyFavoriteActionView.as_view(), name='projected_vacancies-ProjectedVacancyFavorite-favorite'),
]

urlpatterns += router.urls
