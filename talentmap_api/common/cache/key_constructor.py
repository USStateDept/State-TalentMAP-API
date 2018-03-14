import hashlib
import json

from rest_framework_extensions.key_constructor import bits
from rest_framework_extensions.key_constructor.constructors import DefaultKeyConstructor

from talentmap_api.common.common_helpers import order_dict


class PathKeyBit(bits.QueryParamsKeyBit):
    """
    Adds query path as a key bit
    """

    def get_source_dict(self, params, view_instance, view_method, request, args, kwargs):
        return {"path": request.path}


class TalentMAPKeyConstructor(DefaultKeyConstructor):
    """
    Construct the cache key, include query params as a bit
    """
    path_bit = PathKeyBit()
    request_params = bits.QueryParamsKeyBit()

    def prepare_key(self, key_dict):  # nosec We're OK to use MD5 here since it isn't for cryptographic purposes
        key_dict = order_dict(key_dict)  # We order the dict to ensure something like ?q=german&code=1 == ?code=1&q=german
        key_dict = json.dumps(key_dict)
        key_hex = hashlib.md5(key_dict.encode('utf-8')).hexdigest()
        return key_hex


key_func = TalentMAPKeyConstructor()
