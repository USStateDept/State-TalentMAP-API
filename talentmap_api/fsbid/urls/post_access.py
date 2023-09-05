from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import search_post_access as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^filters/$', views.FSBidPostAccessFiltersView.as_view(), name='FSBid-post-access-filters'),
    url(r'^$', views.FSBidPostAccessListView.as_view(), name='FSBid-post-access-list'),
    url(r'^permissions/$', views.FSBidPostAccessActionView.as_view(), name='FSBid-post-access-action'),
]

urlpatterns += router.urls
