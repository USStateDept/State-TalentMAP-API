from django.conf.urls import url
from rest_framework import routers

from talentmap_api.projected_tandem.views import projected_tandem as views

from talentmap_api.common.urls import get_list

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^favorites/$', views.ProjectedFavoriteTandemListView.as_view(), name='view-tandem-favorite-projected'),
    url(r'^favorites/ids/$', views.ProjectedFavoriteTandemIdsListView.as_view(), name='view-tandem-favorite-projected-ids'),
    url(r'^(?P<pk>[0-9]+)/favorite/$', views.ProjectedFavoriteTandemActionView.as_view(), name='projected-ProjectedVacancyFavorite-tandem-favorite'),
]

urlpatterns += router.urls
