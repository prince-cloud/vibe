from django.http import HttpRequest, HttpResponse
class CustomNoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        response: HttpResponse = self.get_response(request)
        if not (request.path.startswith("/static") or request.path.startswith("/media")):
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        return response