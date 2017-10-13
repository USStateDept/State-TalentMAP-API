from django.conf.urls import url
from rest_framework import routers

from talentmap_api.common.urls import get_list

from talentmap_api.language import views

router = routers.SimpleRouter()
router.register(r'', views.LanguageListView, base_name="language.Language")

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/waivers/$', views.LanguageWaiverHistoryView.as_view({**get_list}), name='language.Language-waiver-list'),
]

urlpatterns += router.urls
