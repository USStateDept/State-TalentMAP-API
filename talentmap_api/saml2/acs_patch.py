# Copyright (C) 2010-2013 Yaco Sistemas (http://www.yaco.es)
# Copyright (C) 2009 Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Monkeypatch for consumer service to provide redirect url with user's expiring token
'''
import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from saml2 import BINDING_HTTP_POST
from saml2.sigver import MissingKey
from saml2.response import (
    StatusError, StatusAuthnFailed, SignatureError, StatusRequestDenied,
    UnsolicitedResponse, AuthnResponse
)
from saml2.validate import ResponseLifetimeExceed, ToEarly

from djangosaml2.cache import IdentityCache, OutstandingQueriesCache
from djangosaml2.conf import get_config
from djangosaml2.overrides import Saml2Client
from djangosaml2.signals import post_authenticated
from djangosaml2.utils import (
    fail_acs_response, get_custom_setting
)

from djangosaml2.views import _set_subject_id
from rest_framework_expiring_authtoken.models import ExpiringToken

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def assertion_consumer_service(request,
                               config_loader_path=None,
                               attribute_mapping=None,
                               create_unknown_user=None):
    """SAML Authorization Response endpoint
    The IdP will send its response to this view, which
    will process it with pysaml2 help and log the user
    in using the custom Authorization backend
    djangosaml2.backends.Saml2Backend that should be
    enabled in the settings.py
    """
    attribute_mapping = attribute_mapping or get_custom_setting('SAML_ATTRIBUTE_MAPPING', {'uid': ('username', )})
    create_unknown_user = create_unknown_user if create_unknown_user is not None else \
        get_custom_setting('SAML_CREATE_UNKNOWN_USER', True)
    conf = get_config('talentmap_api.settings.config_settings_loader', request)
    try:
        xmlstr = request.POST['SAMLResponse']
    except KeyError:
        logger.warning('Missing "SAMLResponse" parameter in POST data.')
        raise SuspiciousOperation

    client = Saml2Client(conf, identity_cache=IdentityCache(request.session))

    oq_cache = OutstandingQueriesCache(request.session)
    outstanding_queries = oq_cache.outstanding_queries()

    resp_kwargs = {
        "outstanding_queries": outstanding_queries,
        "outstanding_certs": None,
        "allow_unsolicited": client.allow_unsolicited,
        "want_assertions_signed": client.want_assertions_signed,
        "want_assertions_or_response_signed": (client.want_assertions_signed or client.want_response_signed),
        "want_response_signed": client.want_response_signed,
        "return_addrs": client.service_urls(binding=BINDING_HTTP_POST),
        "entity_id": client.config.entityid,
        "attribute_converters": client.config.attribute_converters,
        "allow_unknown_attributes": client.config.allow_unknown_attributes,
        "conv_info": None,
    }

    try:
        response = client._parse_response(xmlstr, AuthnResponse, "assertion_consumer_service", BINDING_HTTP_POST, **resp_kwargs)
        # response = client.parse_authn_request_response(xmlstr, BINDING_HTTP_POST, outstanding_queries)
    except (StatusError, ToEarly):
        logger.exception("Error processing SAML Assertion.")
        return fail_acs_response(request)
    except ResponseLifetimeExceed:
        logger.info("SAML Assertion is no longer valid. Possibly caused by network delay or replay attack.", exc_info=True)
        return fail_acs_response(request)
    except SignatureError:
        logger.info("Invalid or malformed SAML Assertion.", exc_info=True)
        return fail_acs_response(request)
    except StatusAuthnFailed:
        logger.info("Authentication denied for user by IdP.", exc_info=True)
        return fail_acs_response(request)
    except StatusRequestDenied:
        logger.warning("Authentication interrupted at IdP.", exc_info=True)
        return fail_acs_response(request)
    except MissingKey:
        logger.exception("SAML Identity Provider is not configured correctly: certificate key is missing!")
        return fail_acs_response(request)
    except UnsolicitedResponse:
        logger.exception("Received SAMLResponse when no request has been made.")
        return fail_acs_response(request)

    if response is None:
        logger.warning("Invalid SAML Assertion received (unknown error).")
        return fail_acs_response(request, status=400, exc_class=SuspiciousOperation)

    available_attributes = response.ava
    logger.debug(f"Parse SAML response, available attributes: {available_attributes}")

    # Get the user
    user, _ = User.objects.get_or_create(email=available_attributes['name'][0], username=available_attributes['name'][0])  # for some reason this comes back as name
    user.first_name = available_attributes['givenname'][0]
    user.last_name = available_attributes['surname'][0]
    user.save()

    logger.info(f"User {user} authenticated via SSO")

    # logger.debug('Sending the post_authenticated signal')
    # post_authenticated.send_robust(sender=user, session_info=session_info)

    # Get user's token
    token, _ = ExpiringToken.objects.get_or_create(user=user)
    if token and token.expired():
        token.delete()
        token = ExpiringToken.objects.create(user=user)

    token_redirect_url = f"{settings.LOGIN_REDIRECT_URL}?tmApiToken={token.key}"

    return HttpResponseRedirect(token_redirect_url)
