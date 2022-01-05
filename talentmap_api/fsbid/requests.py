from django.conf import settings

CERT = settings.HRONLINE_CERT
if CERT:
    import requests as r
    requests = r.Session()
    requests.verify = CERT
else:
    import requests
    # TODO - figure out why this breaks tests
    # import requests as r
    # requests = r.Session()
    # requests.verify = False
