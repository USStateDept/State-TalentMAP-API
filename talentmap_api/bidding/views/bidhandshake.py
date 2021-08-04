import logging
import coreapi
import pydash

from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.schemas import AutoSchema
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_condition import Or

from talentmap_api.bidding.serializers import BidHandshakeSerializer, BidHandshakeOfferSerializer
import talentmap_api.cdo.services.available_bidders as services
from talentmap_api.bidding.models import BidHandshake

from talentmap_api.user_profile.models import UserProfile

from talentmap_api.common.mixins import FieldLimitableSerializerMixin
from talentmap_api.common.common_helpers import in_group_or_403, bidderHandshakeNotification, cdoHandshakeNotification, bureauHandshakeNotification
from talentmap_api.common.permissions import isDjangoGroupMember
import talentmap_api.fsbid.services.client as client_services
import talentmap_api.fsbid.services.employee as empservices
import talentmap_api.fsbid.services.available_positions as ap_services

logger = logging.getLogger(__name__)


class BidHandshakeBureauActionView(FieldLimitableSerializerMixin,
                                       GenericViewSet,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin):
    '''
    add, remove, update a Bid Handshake instance
    '''
    serializer_class = BidHandshakeOfferSerializer
    permission_classes = [Or(isDjangoGroupMember('bureau_user'), ) ]

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'expiration_date': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description='Expiration date'),
        }))

    def put(self, request, pk, cp_id, **ars):
        '''
        Offers a handshake to a bidder for a cp_id
        '''
        # TODO: should we limit this endpoint to only bidder perdets of those who have actually bid on this cp?
        # Is it worth the extra network request for the extra validation?
        hasBureauPermissions = empservices.has_bureau_permissions(cp_id, self.request.META['HTTP_JWT'])

        if not hasBureauPermissions:
            raise PermissionDenied()

        user = UserProfile.objects.get(user=self.request.user)
        hs = BidHandshake.objects.filter(bidder_perdet=pk, cp_id=cp_id)

        # Revoke any previously offered handshakes for this cp_id
        hsToArchive = BidHandshake.objects.exclude(bidder_perdet=pk).filter(cp_id=cp_id)
        hsToArchive.update(last_editing_user=user, status='R', update_date=datetime.now(), date_revoked=datetime.now())
        expiration = pydash.get(request, 'data.expiration_date')

        if hs.exists():
            # Only use serializer for PUT body data
            serializer = self.serializer_class(hs.first(), data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # If the handshake is re-offered, clear the bidder_status
            hs.update(last_editing_user=user, status='O', bidder_status=None, update_date=datetime.now(),
                date_offered=datetime.now(), expiration_date=expiration)

            bureauHandshakeNotification(pk, cp_id, True, self.request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Only use serializer for PUT body data
            serializer = self.serializer_class(hs.first(), data=request.data, partial=True)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            ap = ap_services.get_available_position(cp_id, self.request.META['HTTP_JWT'])
            bid_cycle_id = pydash.get(ap, 'bidcycle.id')

            BidHandshake.objects.create(last_editing_user=user, owner=user, bidder_perdet=pk, cp_id=cp_id, bid_cycle_id=bid_cycle_id,
                status='O', date_offered=datetime.now(), expiration_date=expiration)

            bureauHandshakeNotification(pk, cp_id, True, self.request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, cp_id, format=None):
        '''
        Revokes a handshake from a bidder for a cp_id
        '''
        hasBureauPermissions = empservices.has_bureau_permissions(cp_id, self.request.META['HTTP_JWT'])

        if not hasBureauPermissions:
            raise PermissionDenied()

        user = UserProfile.objects.get(user=self.request.user)
        hs = BidHandshake.objects.filter(bidder_perdet=pk, cp_id=cp_id)

        if not hs.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            user = UserProfile.objects.get(user=self.request.user)
            hs.update(last_editing_user=user, bidder_perdet=pk, cp_id=cp_id, status='R',
                update_date=datetime.now(), date_revoked=datetime.now())
            bureauHandshakeNotification(pk, cp_id, False, self.request.META['HTTP_JWT'])
            return Response(status=status.HTTP_204_NO_CONTENT)


class BidHandshakeCdoActionView(FieldLimitableSerializerMixin,
                                       GenericViewSet,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin):
    '''
    update a Bid Handshake instance
    '''
    serializer_class = BidHandshakeSerializer
    permission_classes = [Or(isDjangoGroupMember('cdo'), ) ]

    def put(self, serializer, pk, cp_id, **ars):
        '''
        CDO accepts a handshake for a bidder for a cp_id
        '''
        user = UserProfile.objects.get(user=self.request.user)
        hs = BidHandshake.objects.filter(bidder_perdet=pk, cp_id=cp_id)

        if not BidHandshake.objects.filter(bidder_perdet=pk, cp_id=cp_id, status__in=['O', 'A', 'D']).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            hs.update(last_editing_bidder=user, status='A', bidder_status='A', is_cdo_update=True,
                update_date=datetime.now(), date_accepted=datetime.now())
            cdoHandshakeNotification(pk, cp_id, True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, pk, cp_id, format=None):
        '''
        CDO declines a handshake for a bidder for a cp_id
        '''
        user = UserProfile.objects.get(user=self.request.user)
        hs = BidHandshake.objects.filter(bidder_perdet=pk, cp_id=cp_id)

        if not BidHandshake.objects.filter(bidder_perdet=pk, cp_id=cp_id, status__in=['O', 'A', 'D']).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            hs.update(last_editing_bidder=user, status='D', bidder_status='D', is_cdo_update=True,
                update_date=datetime.now(), date_declined=datetime.now())
            cdoHandshakeNotification(pk, cp_id, False)
            return Response(status=status.HTTP_204_NO_CONTENT)


class BidHandshakeBidderActionView(FieldLimitableSerializerMixin,
                                       GenericViewSet,
                                       mixins.ListModelMixin,
                                       mixins.RetrieveModelMixin):
    '''
    update a Bid Handshake instance
    '''
    serializer_class = BidHandshakeSerializer
    permission_classes = [Or(isDjangoGroupMember('bidder'), ) ]

    def put(self, serializer, cp_id, **ars):
        '''
        Bidder accepts a handshake for a cp_id
        '''
        user = UserProfile.objects.get(user=self.request.user)
        hs = BidHandshake.objects.filter(bidder_perdet=user.emp_id, cp_id=cp_id)
        jwt = self.request.META['HTTP_JWT']

        if not BidHandshake.objects.filter(bidder_perdet=user.emp_id, cp_id=cp_id, status__in=['O', 'A', 'D']).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            hs.update(last_editing_bidder=user, status='A', bidder_status='A', is_cdo_update=False,
                update_date=datetime.now(), date_accepted=datetime.now())
            bidderHandshakeNotification(hs.first().owner, cp_id, user.emp_id, jwt, True)
            return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, cp_id, format=None):
        '''
        Bidder declines handshake for a cp_id
        '''
        user = UserProfile.objects.get(user=self.request.user)
        hs = BidHandshake.objects.filter(bidder_perdet=user.emp_id, cp_id=cp_id)
        jwt = self.request.META['HTTP_JWT']

        if not BidHandshake.objects.filter(bidder_perdet=user.emp_id, cp_id=cp_id, status__in=['O', 'A', 'D']).exists():
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            hs.update(last_editing_bidder=user, status='D', bidder_status='D', is_cdo_update=False,
                update_date=datetime.now(), date_declined=datetime.now())
            bidderHandshakeNotification(hs.first().owner, cp_id, user.emp_id, jwt, False)
            return Response(status=status.HTTP_204_NO_CONTENT)
