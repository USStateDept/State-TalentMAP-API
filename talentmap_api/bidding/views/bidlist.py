import datetime

from django.shortcuts import get_object_or_404

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.bidding.serializers import BidSerializer
from talentmap_api.bidding.models import Bid, BidCycle
from talentmap_api.user_profile.models import UserProfile


class BidListView(mixins.ListModelMixin,
                  GenericViewSet):
    '''
    list:
    Lists all bids for the user's current bidlist
    '''
    serializer_class = BidSerializer
    permission_classes = (IsAuthenticated,)

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
            return Response({"detail": "Submitted bid limit exceeded."}, status=status.HTTP_406_NOT_ACCEPTABLE)

        bid = get_object_or_404(Bid, user=user, id=pk)
        bid.status = Bid.Status.submitted
        bid.submission_date = datetime.datetime.now()
        bid.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
