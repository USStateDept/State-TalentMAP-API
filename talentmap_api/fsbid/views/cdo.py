from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.fsbid.views.base import BaseView
import talentmap_api.fsbid.services.bid as services
import talentmap_api.fsbid.services.cdo as cdoServices

import logging
logger = logging.getLogger(__name__)

class FSBidCDOListView(BaseView):

    def get(self, request):
        '''
        Gets all cdos
        '''
        return Response(cdoServices.cdo(request.META['HTTP_JWT']))


class FSBidCDOView(BaseView):

    def get(self, request, pk):
        '''
        Gets a single cdo by client's perdet_seq_num
        '''
        return Response(cdoServices.single_cdo(request.META['HTTP_JWT'], pk))


class FSBidListView(BaseView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, client_id):
        '''
        Gets all bids for the client user
        '''
        return Response({ "results": services.user_bids(client_id, request.META['HTTP_JWT'])})


class FSBidListBidActionView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def put(self, request, pk, client_id):
        '''
        Submits a bid (sets status to A)
        '''
        try:
            services.submit_bid_on_position(client_id, pk, request.META['HTTP_JWT'])
            user = UserProfile.objects.get(user=self.request.user)
            try:
                owner = UserProfile.objects.get(emp_id=client_id)
            except ObjectDoesNotExist:
                logger.info(f"User with emp_id={client_id} did not exist. No notification created for submitting bid on position id={pk}.")
                return Response(status=status.HTTP_204_NO_CONTENT)

            Notification.objects.create(owner=owner,
                                        tags=['bidding'],
                                        message=f"Bid on position id={pk} has been submitted by CDO {user}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=e)


class FSBidListPositionActionView(BaseView):
    '''
    list:
    Lists all bids for the clients's current bidlist
    '''
    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def get(self, request, pk, client_id, format=None):
        '''
        Indicates if the position is in the client's bidlist

        Returns 204 if the position is in the list, otherwise, 404
        '''
        if len(services.user_bids(client_id, request.META['HTTP_JWT'], pk)) > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk, client_id, format=None):
        '''
        Adds a cycle position to the client's bid list
        '''
        services.bid_on_position(client_id, pk, request.META['HTTP_JWT'])
        user = UserProfile.objects.get(user=self.request.user)
        try:
            owner = UserProfile.objects.get(emp_id=client_id)
        except ObjectDoesNotExist:
            logger.info(f"User with emp_id={client_id} did not exist. No notification created for adding bid on position id={pk}.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        Notification.objects.create(owner=owner,
                                        tags=['bidding'],
                                        message=f"Bid on position id={pk} has been added to your bid list by CDO {user}")
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, client_id, format=None):
        '''
        Closes or deletes specified bid on a cycle position
        '''
        services.remove_bid(client_id, pk, request.META['HTTP_JWT'])
        user = UserProfile.objects.get(user=self.request.user)
        try:
            owner = UserProfile.objects.get(emp_id=client_id)
        except ObjectDoesNotExist:
            logger.info(f"User with emp_id={client_id} did not exist. No notification created for removing bid on position id={pk}.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        Notification.objects.create(owner=owner,
                                        tags=['bidding'],
                                        message=f"Bid on position id={pk} has been removed from your bid list by CDO {user}")
        return Response(status=status.HTTP_204_NO_CONTENT)
