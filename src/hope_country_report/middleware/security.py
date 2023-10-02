class SecurityHeadersMiddleware(object):
    """
    Ensure that we have proper security headers set
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "X-Frame-Options" not in response:  # pragma: no cover
            response["X-Frame-Options"] = "sameorigin"
        if "X-Content-Type-Options" not in response:  # pragma: no cover
            response["X-Content-Type-Options"] = "nosniff"
        if "X-XSS-Protection" not in response:  # pragma: no cover
            response["X-XSS-Protection"] = "1; mode=block"
        return response
