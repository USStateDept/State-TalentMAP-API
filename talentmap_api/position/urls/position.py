from rest_framework import routers
from django.conf.urls import url

from talentmap_api.position import views
from talentmap_api.common.urls import get_list, get_retrieve

router = routers.SimpleRouter()
router.register(r'', views.PositionListView, base_name="position.Position")

urlpatterns = [
    url(r'^favorites/$', views.PositionFavoriteListView.as_view(get_list), name='view-favorite-positions'),
]

urlpatterns += router.urls
