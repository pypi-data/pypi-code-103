import json

from tuhls_core.utils import request_to_ip

from .models import Request


class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.user
            and hasattr(request.user, "gid")
            and hasattr(request.resolver_match, "url_name")
            and request.resolver_match.url_name in ["number_check"]
        ):
            Request.objects.create(
                user=request.user.gid,
                method=request.method,
                status=response.status_code,
                ip=request_to_ip(request),
                request_data=json.dumps(request.GET.__getstate__(), indent=4),
                response_data=json.dumps(response.data, indent=4),
            )
            # print(f"Request URL: {request.get_raw_uri()}")
            # print(f"Request HEADERS: {request.headers}")
            # print(f"Request POST data: {request.POST}")
            # print(f"Request FILES data: {request.FILES}")
            #
            # try:
            #     print(f"Response MEDIA_TYPE: {response.accepted_media_type}")
            #     print(f"Response _MEDIA_TYPE: {response.charset}")
            # except:
            #     print(f"Response MEDIA_TYPE: {response.charset}")
            #     try:
            #         print(f"Response DATA: {response.content}")
            #     except:
            #         print(f"Response DATA: {response.streaming_content}")

        return response
