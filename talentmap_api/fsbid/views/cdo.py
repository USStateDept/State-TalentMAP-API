import logging

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.cdo.models import AvailableBidders
from talentmap_api.messaging.models import Notification
from talentmap_api.common.permissions import isDjangoGroupMember
from talentmap_api.fsbid.views.base import BaseView
from talentmap_api.common.common_helpers import send_email, registeredHandshakeNotification
import talentmap_api.fsbid.services.bid as services
import talentmap_api.fsbid.services.cdo as cdoServices
import talentmap_api.fsbid.services.classifications as classifications_services

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
        return Response({"results": services.user_bids(client_id, request.META['HTTP_JWT'])})


class FSBidBidClientListCSVView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request, client_id, **kwargs):
        '''
        Exports all bids for the client's user to CSV
        '''
        return services.get_user_bids_csv(client_id, request.META['HTTP_JWT'])


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
                owner = UserProfile.objects.filter(emp_id=client_id).first()
            except ObjectDoesNotExist:
                logger.info(f"User with emp_id={client_id} did not exist. No notification created for submitting bid on position id={pk}.")
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            message = f"Bid on a position has been submitted by CDO {user}."

            if owner:
                Notification.objects.create(owner=owner,
                                            tags=['bidding'],
                                            message=message)
                send_email(subject=message, body='Navigate to TalentMAP to see your updated bid tracker.', recipients=[owner.user.email])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=e)


class FSBidListBidRegisterView(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def put(self, request, pk, client_id):
        '''
        Registers a bid
        '''
        jwt = request.META['HTTP_JWT']

        try:
            services.register_bid_on_position(client_id, pk, jwt)
            user = UserProfile.objects.get(user=self.request.user)
            try:
                owner = UserProfile.objects.filter(emp_id=client_id).first()
                message = f"Bid on position has been registered by CDO {user}"

                # Generate a notification
                if owner:
                    Notification.objects.create(owner=owner,
                                                tags=['bidding'],
                                                message=message)
                    send_email(subject=message, body='Navigate to TalentMAP to see your updated bid tracker.', recipients=[owner.user.email])
            except ObjectDoesNotExist:
                logger.info(f"User with emp_id={client_id} did not exist. No notification created for registering bid on position id={pk}.")
                return Response(status=status.HTTP_204_NO_CONTENT)
            finally:
                # Remove the bidder from the available bidders list
                ab = AvailableBidders.objects.filter(bidder_perdet=client_id)
                if ab.exists():
                    ab.first().delete()
                
                # Notify other bidders
                registeredHandshakeNotification(pk, jwt, client_id, True)

            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=e)

    def delete(self, request, pk, client_id):
        '''
        Unregisters a bid
        '''
        jwt = request.META['HTTP_JWT']
        try:
            services.unregister_bid_on_position(client_id, pk, jwt)
            user = UserProfile.objects.get(user=self.request.user)
            try:
                owner = UserProfile.objects.filter(emp_id=client_id).first()
            except ObjectDoesNotExist:
                logger.info(f"User with emp_id={client_id} did not exist. No notification created for unregistering bid on position id={pk}.")
                return Response(status=status.HTTP_204_NO_CONTENT)

            if owner:
                Notification.objects.create(owner=owner,
                                            tags=['bidding'],
                                            message=f"Bid on position has been unregistered by CDO {user}")
            # Notify other bidders
            registeredHandshakeNotification(pk, jwt, client_id, False)
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
            owner = UserProfile.objects.filter(emp_id=client_id).first()
        except ObjectDoesNotExist:
            logger.info(f"User with emp_id={client_id} did not exist. No notification created for adding bid on position id={pk}.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        if owner:
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
            owner = UserProfile.objects.filter(emp_id=client_id).first()
        except ObjectDoesNotExist:
            logger.info(f"User with emp_id={client_id} did not exist. No notification created for removing bid on position id={pk}.")
            return Response(status=status.HTTP_204_NO_CONTENT)
        if owner:
            Notification.objects.create(owner=owner,
                                        tags=['bidding'],
                                        message=f"Bid on position id={pk} has been removed from your bid list by CDO {user}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class FSBidClientEditClassifications(APIView):

    permission_classes = (IsAuthenticated, isDjangoGroupMember('cdo'),)

    def put(self, request, client_id):
        '''
        Inserts/Deletes the classifications for the client
        '''
        try:
            id = []
            if request.data['insert']:
                id = classifications_services.insert_client_classification(request.META['HTTP_JWT'], client_id, request.data['insert'])
            if request.data['delete']:
                id = classifications_services.delete_client_classification(request.META['HTTP_JWT'], client_id, request.data['delete'])
            return Response(status=status.HTTP_200_OK, data=id)
        except Exception as e:
            return Response(status=status.HTTP_422_UNPROCESSABLE_ENTITY, data=e)
