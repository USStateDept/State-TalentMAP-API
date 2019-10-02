
class IE11Middleware:
    '''
    Informs the  browser not to use browser-side caching for API responses.
    This resolves an issue where the front end was unable to retrieve fresh data.
    '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = "no-cache,no-store"
        return response

class ExposeHeadersMiddleware:
    '''
    Informs the browser to allow the reading of certain headers.
    '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Access-Control-Expose-Headers'] = "Content-Disposition"
        return response
