import logging
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from rest_framework_extensions.cache.decorators import CacheResponse as cache_response

logger = logging.getLogger('console')


class CachedViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    GenericViewSet):

    @cache_response()
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @cache_response()
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
