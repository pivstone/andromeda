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
            response = http.JsonResponse(status=exception.status, data=exception.errors())
            return response
