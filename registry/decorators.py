from django.utils.decorators import available_attrs
from functools import wraps
from hashlib import sha256, sha512, sha384
from registry.crypto import DigestCheck
from rest_framework.request import Request
from django.http import HttpRequest

__author__ = 'pivstone'

hash_map = {"sha256": sha256, "sha512": sha512, "sha384": sha384}


def digest_hash():
    def decorators(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(*args, **kwargs):
            for arg in args:
                if isinstance(arg, (Request, HttpRequest)):
                    check = DigestCheck(arg)
                    check.verify()
            response = func(*args, **kwargs)
            if response.status_code == 200:
                builder = sha256()
                builder.update(response.content)
                digest = "sha256:%s" % builder.digest().hex()
                response['Etag'] = digest
                response['Docker-Content-Digest '] = digest
            return response

        return inner

    return decorators
