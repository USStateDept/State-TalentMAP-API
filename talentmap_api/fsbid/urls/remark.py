from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import remark as views

router = routers.SimpleRouter()

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.RemarkView.as_view(), name="remark"),
    url(r'^/$', views.RemarkActionView.as_view(), name="remark-action"),
]

urlpatterns += router.urls
