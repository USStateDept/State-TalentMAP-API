from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import panel as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^dates/$', views.PanelDatesView.as_view(), name='panel-FSBid-dates'),
    url(r'^categories/$', views.PanelCategoriesView.as_view(), name='panel-FSBid-categories'),
]

urlpatterns += router.urls
