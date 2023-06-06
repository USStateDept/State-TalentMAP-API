from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import admin_panel as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^remark/$', views.CreateRemarkView.as_view(), name='administration.createremark'),
]

urlpatterns += router.urls
