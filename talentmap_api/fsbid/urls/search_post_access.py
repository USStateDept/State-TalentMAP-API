from django.conf.urls import url
from rest_framework import routers

from talentmap_api.fsbid.views import search_post_access as views

router = routers.SimpleRouter()
urlpatterns = [
    url(r'^filters/$', views.FSBidSearchPostAccessViewFilters.as_view(), name='FSBid-search-post-access-filters'),
    url(r'^data/$', views.FSBidSearchPostAccessActionView.as_view(), name='FSBid-search-post-access-data'),
    url(r'^remove/$', views.FSBidSearchPostAccessRemoveActionView.as_view(), name='FSBid-search-post-access-remove'),
]

urlpatterns += router.urls
