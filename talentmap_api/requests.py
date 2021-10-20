from django.conf import settings

CERT = settings.HRONLINE_CERT
if CERT:
    import requests as r
    requests = r.Session()
    requests.verify = CERT
else:
    import requests