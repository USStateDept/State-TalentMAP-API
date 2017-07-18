from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from talentmap_api.user_profile.models import UserProfile
from talentmap_api.user_profile.serializers import UserProfileSerializer


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
