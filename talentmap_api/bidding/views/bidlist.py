from dateutil.relativedelta import relativedelta

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils import timezone

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.bidding.serializers.serializers import BidSerializer
from talentmap_api.bidding.models import Bid, BidCycle
from talentmap_api.bidding.filters import BidFilter
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification
from talentmap_api.common.permissions import isDjangoGroupMember

import logging
logger = logging.getLogger(__name__)


class BidListView(mixins.ListModelMixin,
                  GenericViewSet):
    '''
    list:
    Lists all bids for the user's current bidlist
    '''
    serializer_class = BidSerializer
    filter_class = BidFilter
    permission_classes = (IsAuthenticated, isDjangoGroupMember('bidder'),)

    def destroy(self, request, *args, **kwargs):
        '''
        Closes or deletes specified bid

        This endpoint will delete bids which are still in a draft status, but close any other status
        if permitted.
        '''
        user = UserProfile.objects.get(user=self.request.user)
        # Grab the bid in question
        bid = get_object_or_404(Bid, id=kwargs.get("pk"))

        # Are we the owning user?
        is_ours = bid.user.id is user.id
        # Are we the CDO?
        is_direct_report = bid.user.id in user.direct_reports.values_list("id", flat=True)

        if not is_ours and not is_direct_report:
            logger.warning(f"User {self.request.user.id}:{self.request.user} attempted to remove bid {bid} but does not own and is not CDO for owner")
            raise PermissionDenied

        # If we're the CDO, we can close it regardless of status/date restrictions
        if is_direct_report:
            bid.status = Bid.Status.closed
            bid.save()
            Notification.objects.create(owner=bid.user,
                                        tags=['bidding'],
                                        message=f"Bid {bid} has been closed by CDO {user}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif timezone.now() < bid.bidcycle.cycle_deadline_date:
            if bid.status in [Bid.Status.draft, Bid.Status.submitted]:
                bid.status = Bid.Status.closed
                bid.save()
                logger.info(f"User {user.user.id}:{user.user} closed bid {bid}")
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                # We are either outside of the permittable date range for self-closing,
                # or we are looking at a status that requires CDO action (i.e. handshake)
                logger.info(f"User {user.user.id}:{user.user} attempted to close bid {bid}, but is not CDO and is outside of permissable date range for closing bids without CDO approval")
                raise PermissionDenied
        else:
            # We're not CDO, and we're after the deadline
            logger.info(f"User {user.user.id}:{user.user} attempted to close bid {bid} but is outside of permissable date range")
            raise PermissionDenied

    def get_queryset(self):
        queryset = UserProfile.objects.get(user=self.request.user).bidlist.all()
        queryset = self.serializer_class.prefetch_model(Bid, queryset)
        return queryset


class BidListPositionActionView(APIView):
    def get(self, request, pk, format=None):
        '''
        Indicates if the position is in the user's bidlist

        Returns 204 if the position is in the list, otherwise, 404
        '''
        if UserProfile.objects.get(user=self.request.user).bidlist.filter(position__id=pk).count() > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, format=None):
        '''
        Adds a position to the user's bid list
        '''
        bidcycle = BidCycle.objects.filter(active=True).latest("cycle_start_date")
        position = get_object_or_404(bidcycle.positions.all(), id=pk)

        # Position must not already have a handshake or greater bid status
        if not position.can_accept_new_bids(bidcycle)[0]:
            return Response("Cannot bid on a position that already has a qualifying bid", status=status.HTTP_400_BAD_REQUEST)

        # For now, we use whatever the latest active bidcycle is
        bid = Bid.objects.get_or_create(bidcycle=bidcycle,
                                        user=UserProfile.objects.get(user=self.request.user),
                                        position=position)[0]
        user = UserProfile.objects.get(user=self.request.user)

        # User cannot be retiring during the position's tour of duty
        current_assignment = bid.position.current_assignment
        if current_assignment and current_assignment.estimated_end_date + relativedelta(months=bid.position.post.tour_of_duty.months) > user.mandatory_retirement_date:
            return Response("Cannot bid on a position during which the user will retire", status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"User {self.request.user.id}:{self.request.user} creating draft bid {bid}")
        user.bidlist.add(bid)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from the user's bid list, if that bid is still in draft, submitted, or handshake-offered status
        '''
        bid = get_object_or_404(Bid,
                                user=UserProfile.objects.get(user=self.request.user),
                                position__id=pk)

        if not bid.can_delete:
            return Response("Only draft bids and submitted bids in an active bid cycle can be deleted", status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"User {self.request.user.id}:{self.request.user} deleting bid {bid}")
        bid.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
