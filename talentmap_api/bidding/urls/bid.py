from django.conf.urls import url

from talentmap_api.common.urls import patch_update
from talentmap_api.bidding.views import bid as views

urlpatterns = [
    # RC-1 Disabled
    # url(r'^(?P<pk>[0-9]+)/submit/$', views.BidListBidderActionView.as_view({'get': 'submit'}), name='bidding.Bid-bid-actions-submit'),
    url(r'^(?P<pk>[0-9]+)/accept_handshake/$', views.BidListBidderActionView.as_view({'get': 'accept_handshake'}), name='bidding.Bid-bid-actions-accept-handshake'),
    url(r'^(?P<pk>[0-9]+)/decline_handshake/$', views.BidListBidderActionView.as_view({'get': 'decline_handshake'}), name='bidding.Bid-bid-actions-decline-handshake'),

    # AO actions
    # RC-1 Disabled
    # url(r'^(?P<pk>[0-9]+)/schedule_panel/$', views.BidUpdateView.as_view(patch_update), name='bidding.Bid-bid-update'),
    # url(r'^(?P<pk>[0-9]+)/approve/$', views.BidListAOActionView.as_view({'get': 'approve'}), name='bidding.Bid-bid-ao-approve'),
    # url(r'^(?P<pk>[0-9]+)/decline/$', views.BidListAOActionView.as_view({'get': 'decline'}), name='bidding.Bid-bid-ao-decline'),
    # url(r'^(?P<pk>[0-9]+)/offer_handshake/$', views.BidListAOActionView.as_view({'get': 'offer_handshake'}), name='bidding.Bid-bid-ao-offer-handshake'),
    # url(r'^(?P<pk>[0-9]+)/self_assign/$', views.BidListAOActionView.as_view({'get': 'self_assign'}), name='bidding.Bid-bid-ao-self-assign'),
]
