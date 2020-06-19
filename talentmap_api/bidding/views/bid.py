from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status

from talentmap_api.common.common_helpers import in_group_or_403
from talentmap_api.common.permissions import isDjangoGroupMember

from talentmap_api.bidding.serializers.serializers import BidWritableSerializer
from talentmap_api.bidding.models import Bid
from talentmap_api.user_profile.models import UserProfile

import logging
logger = logging.getLogger(__name__)


class BidUpdateView(mixins.UpdateModelMixin,
                    GenericViewSet):
    '''
    partial_update:
    Update the specified bid panel date
    '''
    serializer_class = BidWritableSerializer
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))

    def perform_update(self, serializer):
        instance = serializer.save(status=Bid.Status.in_panel, in_panel_date=timezone.now())
        logger.info(f"User {self.request.user.id}:{self.request.user} setting status for bid {instance} to in_panel")

    def get_object(self):
        bid = get_object_or_404(Bid, pk=self.request.parser_context.get("kwargs").get("pk"), status__in=[Bid.Status.handshake_accepted, Bid.Status.in_panel])
        in_group_or_403(self.request.user, f'bureau_ao:{bid.position.position.bureau.code}')
        return bid


class BidListAOActionView(GenericViewSet):
    '''
    Supports all AO actions for bids
    '''

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bureau_ao'))

    def set_bid_status(self, user, bid_id, status, prereq_status=None):
        bid = get_object_or_404(Bid, id=bid_id)
        # If we have a prerequisite status, ensure we have a matching bid
        if prereq_status:
            bid = get_object_or_404(Bid, id=bid_id, status=prereq_status)
        # We must be an AO for the bureau for the bid's position
        in_group_or_403(user, f'bureau_ao:{bid.position.position.bureau.code}')

        logger.info(f"User {self.request.user.id}:{self.request.user} setting bid status for {bid} to {status}")
        bid.status = status
        setattr(bid, f"{status}_date", timezone.now())
        bid.save()

    def approve(self, request, pk, format=None):
        '''
        Approves a bid

        Returns 204 if the action is a success
        '''
        self.set_bid_status(self.request.user, pk, Bid.Status.approved, Bid.Status.in_panel)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def decline(self, request, pk, format=None):
        '''
        Declines a bid

        Returns 204 if the action is a success
        '''
        self.set_bid_status(self.request.user, pk, Bid.Status.declined)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def offer_handshake(self, request, pk, format=None):
        '''
        Offers a handshake on a bid

        Returns 204 if the action is a success
        '''
        self.set_bid_status(self.request.user, pk, Bid.Status.handshake_offered, Bid.Status.submitted)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def self_assign(self, request, pk, format=None):
        '''
        Assigns the current user as the specified bid's reviewer

        Returns 204 if the action is a success
        '''
        bid = get_object_or_404(Bid, id=pk)
        # We must be an AO for the bureau for the bid's position
        in_group_or_403(self.request.user, f'bureau_ao:{bid.position.position.bureau.code}')

        logger.info(f"User {self.request.user.id}:{self.request.user} self-assigning to bid {bid}")
        bid.reviewer = self.request.user.profile
        bid.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BidListBidderActionView(GenericViewSet):
    '''
    Supports all bidder actions for a bid
    '''

    permission_classes = (IsAuthenticated, isDjangoGroupMember('bidder'),)

    def submit(self, request, pk, format=None):
        '''
        Submits a bid

        Returns 204 if the action is a success
        '''
        # First, validate that the user has not exceeded their maximum allotted bids
        user = UserProfile.objects.get(user=self.request.user)
        bid = get_object_or_404(Bid, user=user, id=pk, status=Bid.Status.draft)
        if user.bidlist.filter(status=Bid.Status.submitted, bidcycle=bid.bidcycle).count() >= Bid.MAXIMUM_SUBMITTED_BIDS:
            return Response({"detail": "Submitted bid limit exceeded."}, status=status.HTTP_400_BAD_REQUEST)
        if user.bidlist.filter(is_priority=True, bidcycle=bid.bidcycle).exists():
            return Response({"detail": "Cannot submit a bid when another bid has priority."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"User {self.request.user.id}:{self.request.user} is submitting bid {bid}")
        bid.status = Bid.Status.submitted
        bid.submitted_date = timezone.now()
        bid.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def accept_handshake(self, request, pk, format=None):
        '''
        Accepts a handshake for a bid

        Returns 204 if the action is a success
        '''
        user = UserProfile.objects.get(user=self.request.user)
        bid = get_object_or_404(Bid, user=user, id=pk, status=Bid.Status.handshake_offered)
        if user.bidlist.filter(is_priority=True, bidcycle=bid.bidcycle).exists():
            return Response({"detail": "Cannot submit a bid when another bid has priority."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"User {self.request.user.id}:{self.request.user} is accepting handshake on bid {bid}")
        bid.status = Bid.Status.handshake_accepted
        bid.handshake_accepted_date = timezone.now()
        bid.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def decline_handshake(self, request, pk, format=None):
        '''
        Declines a handshake for a bid

        Returns 204 if the action is a success
        '''
        bid = get_object_or_404(Bid, user=UserProfile.objects.get(user=self.request.user), id=pk, status=Bid.Status.handshake_offered)
        logger.info(f"User {self.request.user.id}:{self.request.user} is declining handshake on bid {bid}")
        bid.status = Bid.Status.handshake_declined
        bid.handshake_declined_date = timezone.now()
        bid.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
