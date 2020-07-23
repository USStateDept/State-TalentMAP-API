import logging

from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly

import talentmap_api.fsbid.services.common as common

logger = logging.getLogger(__name__)


class BaseView(APIView):

    permission_classes = (IsAuthenticatedOrReadOnly,)
    uri = ""
    mapping_function = None
    mod_function = None

    @classmethod
    def get_extra_actions(cls):
        return []

    def get(self, request):

        results = common.get_fsbid_results(self.uri, request.META['HTTP_JWT'], self.mapping_function)
        if results is None:
            logger.warning(f"Invalid response from '\{self.uri}'.")
            return Response({"detail": "FSBID returned error."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if callable(self.mod_function):
            results = self.mod_function(results)

        return Response(results)
