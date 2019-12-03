import requests
import logging
import jwt
import talentmap_api.fsbid.services.common as services
from django.conf import settings

API_ROOT = settings.FSBID_API_URL

logger = logging.getLogger(__name__)

