import datetime

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.bidding.serializers import BidSerializer
from talentmap_api.bidding.models import Bid, BidCycle
from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification


class BidListView(mixins.ListModelMixin,
                  GenericViewSet):
    '''
    list:
    Lists all bids for the user's current bidlist
    '''
    serializer_class = BidSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        '''
        Closes or deletes specified bid

        This endpoint will delete bids which are still in a draft status, but close any other status
        if permitted.
        '''
        user = UserProfile.objects.get(user=self.request.user)
        # Grab the bid in question
        bid = get_object_or_404(Bid, id=kwargs.get("pk"), status__in=[Bid.Status.submitted, Bid.Status.draft])

        # Are we the owning user?
        is_ours = bid.user.id is user.id
        # Are we the CDO?
        is_direct_report = bid.user.id in user.direct_reports.values_list("id", flat=True)

        if not is_ours and not is_direct_report:
            raise PermissionDenied

        # If today's date is before the deadline date, we can delete/close in either situation
        if datetime.datetime.now().date() < bid.bidcycle.cycle_deadline_date:
            if bid.status == Bid.Status.draft:
                bid.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            elif bid.status == Bid.Status.submitted:
                bid.status = Bid.Status.closed
                bid.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        # If we're after the date and we're CDO, we can close the bid
        elif is_direct_report:
            bid.status = Bid.Status.closed
            bid.save()
            Notification.objects.create(owner=bid.user,
                                        message=f"Bid {bid} has been closed by CDO {user}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
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

        # For now, we use whatever the latest active bidcycle is
        bid = Bid.objects.get_or_create(bidcycle=bidcycle,
                                        user=UserProfile.objects.get(user=self.request.user),
                                        position=position)[0]
        UserProfile.objects.get(user=self.request.user).bidlist.add(bid)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, format=None):
        '''
        Removes the position from the user's bid list, if that bid is still in draft status
        '''
        bid = get_object_or_404(Bid,
                                user=UserProfile.objects.get(user=self.request.user),
                                position__id=pk,
                                status=Bid.Status.draft)
        bid.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BidListBidSubmitView(APIView):
    def put(self, request, pk, format=None):
        '''
        Submits the specified bid
        '''
        # First, validate that the user has not exceeded their maximum alloted bids
        user = UserProfile.objects.get(user=self.request.user)
        if user.bidlist.filter(status=Bid.Status.submitted).count() >= Bid.MAXIMUM_SUBMITTED_BIDS:
            return Response({"detail": "Submitted bid limit exceeded."}, status=status.HTTP_400_BAD_REQUEST)

        bid = get_object_or_404(Bid, user=user, id=pk)
        bid.status = Bid.Status.submitted
        bid.submission_date = datetime.datetime.now()
        bid.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
