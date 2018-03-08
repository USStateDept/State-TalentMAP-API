from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from rest_framework.permissions import IsAuthenticated

from rest_framework_expiring_authtoken.models import ExpiringToken

from talentmap_api.common.tokens.serializers import TokenSerializer


class TokenView(mixins.RetrieveModelMixin,
                GenericViewSet):
    """
    retrieve:
    Return the current user's authentication token
    """

    serializer_class = TokenSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        token, _ = ExpiringToken.objects.get_or_create(user=self.request.user)
        if token and token.is_expired():
            token.delete()
            token = ExpiringToken.objects.create(user=self.request.user)
        return token
