from rest_framework import routers
from django.conf.urls import url

from talentmap_api.position import views

router = routers.SimpleRouter()
router.register(r'', views.GradeListView, base_name="position.Grade")

urlpatterns = []

urlpatterns += router.urls
