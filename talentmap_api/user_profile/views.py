from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps

from talentmap_api.common.mixins import ActionDependentSerializerMixin, FieldLimitableSerializerMixin

from talentmap_api.user_profile.models import UserProfile, Sharable, SavedSearch
from talentmap_api.user_profile.serializers import (UserProfileSerializer,
                                                    UserProfileWritableSerializer,
                                                    SharableSerializer,
                                                    SavedSearchSerializer)


class UserProfileView(FieldLimitableSerializerMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      ActionDependentSerializerMixin,
                      GenericViewSet):
    """
    retrieve:
    Return the current user profile

    partial_update:
    Update the current user profile
    """
    serializers = {
        "default": UserProfileSerializer,
        "partial_update": UserProfileWritableSerializer
    }

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        queryset = UserProfile.objects.filter(user=self.request.user)
        self.serializer_class.prefetch_model(UserProfile, queryset)
        return queryset.first()


class SavedSearchView(FieldLimitableSerializerMixin,
                      GenericViewSet,
                      mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin):
    '''
    create:
    Creates a new saved share

    partial_update:
    Edits a saved share

    retrieve:
    Retrieves a specific saved share

    list:
    Lists all of the user's saved shares

    destroy:
    Deletes a specified saved search
    '''

    serializer_class = SavedSearchSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)

    def get_queryset(self):
        queryset = SavedSearch.objects.filter(owner=self.request.user.profile)
        self.serializer_class.prefetch_model(SavedSearch, queryset)
        return queryset


class ShareView(FieldLimitableSerializerMixin,
                GenericViewSet,
                mixins.UpdateModelMixin):
    '''
    post:
    Shares a TalentMAP element

    Post method accepts an object with at minimum the following parameters:
    * type - the type of object to be shared (position)
    * id - the id of the object to be shared
    * email - the email to send the share to

    partial_update:
    Update a shared notification

    This method is mainly used to update the read status of a share
    '''

    AVAILABLE_TYPES = {
        "position": "position.Position"
    }

    serializer_class = SharableSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = Sharable.objects.filter(receiving_user=self.request.user.profile)
        self.serializer_class.prefetch_model(Sharable, queryset)
        return queryset

    def post(self, request, format=None):
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
        formatter = None
        if type == "position":
            def formatter(instance):
                return f"This position has been shared with you via TalentMAP\n\n" \
                       f"\tPosition Number: {instance.position_number}\n\tPosition Title: {instance.title}\n" \
                       f"\tPost: {instance.post}"
        return formatter
