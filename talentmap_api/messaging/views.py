from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.apps import apps

from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated

from talentmap_api.common.mixins import FieldLimitableSerializerMixin

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.messaging.models import Notification, Sharable, Task
from talentmap_api.messaging.filters import NotificationFilter, TaskFilter
from talentmap_api.messaging.serializers import NotificationSerializer, SharableSerializer, TaskSerializer


class NotificationView(FieldLimitableSerializerMixin,
                       GenericViewSet,
                       mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin):
    '''
    partial_update:
    Edits a saved notification

    retrieve:
    Retrieves a specific notification

    list:
    Lists all notifications

    destroy:
    Deletes a specified notification
    '''

    serializer_class = NotificationSerializer
    filter_class = NotificationFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Notification.objects.filter(owner=self.request.user.profile)
        self.serializer_class.prefetch_model(Notification, queryset)
        return queryset


class TaskView(FieldLimitableSerializerMixin,
               GenericViewSet,
               mixins.ListModelMixin,
               mixins.RetrieveModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin):
    '''
    partial_update:
    Edits a saved task

    retrieve:
    Retrieves a specific task

    list:
    Lists all tasks

    destroy:
    Deletes a specified task
    '''

    serializer_class = TaskSerializer
    filter_class = TaskFilter
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Task.objects.filter(owner=self.request.user.profile)
        self.serializer_class.prefetch_model(Task, queryset)
        return queryset


class ShareView(FieldLimitableSerializerMixin,
                APIView):

    AVAILABLE_TYPES = {
        "position": "position.Position"
    }

    serializer_class = SharableSerializer
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk):
        '''
        Update a shared notification

        This method is mainly used to update the read status of a share
        '''
        share = get_object_or_404(Sharable, receiving_user=self.request.user.profile, id=pk)
        serializer = self.serializer_class(share, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        '''
        Shares a TalentMAP element

        Post method accepts an object with at minimum the following parameters:
        * type - the type of object to be shared (position)
        * id - the id of the object to be shared
        * email - the email to send the share to
        '''
        valid, error = self.validate(request)
        user = self.request.user

        if valid:
            response = None
            if "@state.gov" in request.data.get("email"):
                response = self.internal_share(user, request.data.get("email"), request.data.get("type"), request.data.get("id"))
            else:
                response = self.email_share(user, request.data.get("email"), request.data.get("type"), request.data.get("id"))
            return response
        else:
            return Response({"message": error}, status=status.HTTP_400_BAD_REQUEST)

    def validate(self, request):
        '''
        Validates that the request is a properly formatted share request, returning (True, None) in that case.
        If the request fails validation, it will return (False, String) where the second item of the tuple is
        a string explanation of the validation error.
        '''
        if "type" not in request.data:
            return (False, "POSTs to this endpoint require the 'type' parameter")
        elif request.data.get("type") not in self.AVAILABLE_TYPES.keys():
            return (False, f"Type must be one of the following: {','.join(self.AVAILABLE_TYPES.keys())}")

        if "id" not in request.data:
            return (False, "id of sharable object must be specified")

        if "email" not in request.data:
            return (False, "E-mail shares require an 'email' parameter to be specified")

        return (True, None)

    def email_share(self, user, email, type, id):
        # Get our e-mail formatter
        formatter = self.get_email_formatter(type)
        instance = None

        # Attempt to get the object instance we want to share
        try:
            instance = apps.get_model(self.AVAILABLE_TYPES[type]).objects.get(id=id)
        except ObjectDoesNotExist:
            # If it doesn't exist, respond with a 404
            return Response({"message": f"Object with id {id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Create our e-mail body
        email_body = {
            "to": email,
            "subject": f"[TalentMAP] Shared {type}",
            "body": formatter(instance)
        }

        # TODO: Implement actual e-mail sending here when avaiable e-mail servers are clarified

        # Return a 202 ACCEPTED with a copy of the email body
        return Response({"message": f"Position shared externally via email at {email}", "email_body": email_body}, status=status.HTTP_202_ACCEPTED)

    def internal_share(self, user, email, type, id):
        receiving_user = None

        # Attempt to get the object instance we want to share
        try:
            apps.get_model(self.AVAILABLE_TYPES[type]).objects.get(id=id)
        except ObjectDoesNotExist:
            # If it doesn't exist, respond with a 404
            return Response({"message": f"Object with id {id} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Attempt to get the receiving user by e-mail address
        try:
            receiving_user = UserProfile.objects.get(user__email=email)
        except ObjectDoesNotExist:
            return Response({"message": f"User with email {email} does not exist"}, status=status.HTTP_404_NOT_FOUND)

        # Create our sharable object using the source user, receiving user, id, and model
        # This will auto-populate in the receiving user's received shares on their profile
        Sharable.objects.create(sharing_user=user.profile,
                                receiving_user=receiving_user,
                                sharable_id=id,
                                sharable_model=self.AVAILABLE_TYPES[type])

        return Response({"message": f"Position shared internally to user with email {email}"}, status=status.HTTP_202_ACCEPTED)

    def get_email_formatter(self, type):
        if type == "position":
            def formatter(instance):
                return f"This position has been shared with you via TalentMAP\n\n" \
                       f"\tPosition Number: {instance.position_number}\n\tPosition Title: {instance.title}\n" \
                       f"\tPost: {instance.post}"
        else:
            formatter = None
        return formatter
