from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.serializers import UserProfileSerializer

from talentmap_api.position.models import Position
from talentmap_api.position.serializers import PositionSerializer


class UserProfileView(ReadOnlyModelViewSet):
    """
    retrieve:
    Return the current user profile
    """

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        queryset = UserProfile.objects.filter(user=self.request.user)
        self.serializer_class.prefetch_model(UserProfile, queryset)
        return queryset.first()


class UserFavoritePositionView(APIView):
    '''
    Interacts with a user's favorited positions
    '''

    model = Position
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        '''
        Returns a user's favorited positions
        '''

        queryset = UserProfile.objects.get(user=request.user).favorite_positions
        queryset = self.serializer_class.prefetch_model(Position, queryset)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def put(self, request, format=None):
        '''
        Adds a position to the current user's favorites
        '''

        position_id = request.data.get("id", None)

        if position_id:
            try:
                position = Position.objects.get(id=position_id)
                profile = UserProfile.objects.get(user=request.user)
                profile.favorite_positions.add(position)
                profile.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            except ObjectDoesNotExist:
                return Response({"message": f"Position with id {position_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Parameter 'id' is required when adding a favorite position"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, format=None):
        '''
        Deletes a position from the current user's favorites
        '''

        position_id = request.data.get("id", None)

        if position_id:
            try:
                position = Position.objects.get(id=position_id)
                profile = UserProfile.objects.get(user=request.user)
                profile.favorite_positions.remove(position)
                profile.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            except ObjectDoesNotExist:
                return Response({"message": f"Position with id {position_id} does not exist"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"message": "Parameter 'id' is required when adding a favorite position"}, status=status.HTTP_400_BAD_REQUEST)
