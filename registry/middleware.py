from django import http
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.cache import patch_vary_headers
from registry.exceptions import RegistryException

__author__ = 'pivstone'


class CustomHeaderMiddleware(object):
    """
    增加自定头
    """

    def process_response(self, request, response):
        for key, value in settings.CUSTOM_HEADERS.items():
            response[key] = value

        return response


class ExceptionsHandleMiddleware(object):
    """
    统一错误返回
    """

    def process_exception(self, request, exception):
        if isinstance(exception, RegistryException):
            response = http.JsonResponse(status=exception.status, data=exception.__str__())
            return response


class Oauth2TokenMiddleware(object):
    def process_request(self, request):
        if request.META.get('HTTP_AUTHORIZATION', '').startswith('Bearer'):
            if not hasattr(request, 'user') or request.user.is_anonymous():
                user = authenticate(request=request)
                if user:
                    request.user = request._cached_user = user
        else:
            response = http.JsonResponse(data={"errors": [
                {"code": "UNAUTHORIZED", "message": "access to the requested resource is not authorized",
                 "detail": [{"Type": "repository", "Name": "samalba/my-app", "Action": "pull"},
                            {"Type": "repository", "Name": "samalba/my-app", "Action": "push"}]}]})
            response[
                'Www-Authenticate'] = 'Bearer realm="http://192.168.233.8/token",service="registry.docker.io",scope="repository:my/lastest:pull,push"'
            response.status_code = 401
            return response

    def process_response(self, request, response):
        patch_vary_headers(response, ('Authorization',))
        return response
