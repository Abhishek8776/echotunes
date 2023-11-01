class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # print("This is executed before the view")

        response = self.get_response(request)

        # print("This is executed after the view")

        return response
