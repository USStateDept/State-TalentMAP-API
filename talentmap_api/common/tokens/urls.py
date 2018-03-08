from django.conf.urls import url

from talentmap_api.common.tokens import views
from talentmap_api.common.urls import get_retrieve

urlpatterns = [
    url(r'^$', views.TokenView.as_view({**get_retrieve}), name='common.Token-retrieve'),
]
