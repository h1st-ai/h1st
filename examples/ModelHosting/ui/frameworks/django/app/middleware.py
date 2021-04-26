def dev_cors_middleware(get_response):
    """
    Adds CORS headers for local testing only to allow the frontend, which is served on
    localhost:3000, to access the API, which is served on localhost:8000.
    """
    def middleware(request):
        response = get_response(request)

        response['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, OPTIONS, DELETE, HEAD'
        response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken'
        response['Access-Control-Allow-Credentials'] = 'true'
        return response
    return middleware