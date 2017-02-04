# coding=utf-8
import json

import base64
import datetime
from django.utils import six
from registry import six as project_six
from ecdsa import VerifyingKey, NIST256p, BadSignatureError, SigningKey
from ecdsa.util import number_to_string
from hashlib import sha256, sha512, sha384
from registry import exceptions


def _decode(value):
    """
    Base64 解码，补齐"="
    记得去错多余的“＝”，垃圾Docker，签发的时候会去掉
    :param value:
    :return:
    """

    length = len(value) % 4
    if length in (2, 3,):
        value += (4 - length) * "="
    elif length != 0:
        raise ValueError("Invalid base64 string")
    if not isinstance(value, six.binary_type):
        value = value.encode()
    return base64.urlsafe_b64decode(value)


def _encode(value):
    """
    Base64 编码
    记得去错多余的“＝”，垃圾Docker，签发的时候会去掉
    :param value:
    :return:
    """
    if not isinstance(value, six.binary_type):
        value = value.encode()
    data_string = base64.urlsafe_b64encode(value)
    # 去错多余的“＝”，垃圾Docker，签发的时候会去掉
    return data_string.decode().replace("=", "").encode()


_crv_mapping = {
    "P-256": NIST256p
}


class SignKey(object):
    def __init__(self):
        sign_key = SigningKey.generate(curve=NIST256p, hashfunc=sha256)
        h = sha256()
        h.update(sign_key.get_verifying_key().to_string())
        dig = h.hexdigest().upper()[:48]
        kid = ""
        for i in range(0, len(dig) // 4):
            kid += dig[i * 4:i * 4 + 4]
            kid += ":"
        kid = kid[:-1]

        x = sign_key.verifying_key.pubkey.point.x()
        y = sign_key.verifying_key.pubkey.point.y()
        order = sign_key.verifying_key.pubkey.order
        x_str = _encode(
            number_to_string(x, order))
        y_str = _encode(
            number_to_string(y, order))

        self.key = sign_key
        if isinstance(x_str, six.binary_type):
            x_str = x_str.decode()
        self.x = x_str

        if isinstance(y_str, six.binary_type):
            y_str = y_str.decode()
        self.y = y_str
        self.kid = kid

    def sign(self, *args, **kwargs):
        return self.key.sign(*args, **kwargs)


_sign_key = SignKey()


def verify_header(context, digest):
    digger = sha256()
    digger.update(context)
    return "sha256:%s" % digger.digest().hex == digest


class DigestCheck(object):
    def __init__(self, request):

        self.digest_head = request.META.get("HTTP_DOCKER_CONTENT_DIGEST", None)

        if self.digest_head:  # content 可能比较大，没有digest 头就不要作死了
            self.content = request.read()

    def verify(self, raise_exception=True):
        if not self.digest_head:
            return True
        try:
            digest_method, digest_value = self.digest_head.split(":")
        except ValueError:
            digest_method = "sha256"
            digest_value = "bad digest"
        digest_func = {"sha256": sha256, "sha512": sha512, "sha384": sha384}[digest_method.lower()]
        h = digest_func()
        h.update(self.content)
        result = h.hexdigest() == digest_value.lower()
        if raise_exception and not result:
            raise exceptions.DigestInvalidException()
        return result


def jws_sign(payload):
    if isinstance(payload, dict):
        payload = json.dumps(payload, indent=4)
    else:
        raise ValueError("Need Dict")
    protected_header = {
        "formatLength": len(payload) - 2,
        "formatTail": _encode(payload[-2:]).decode(),
        "time": project_six.convert2timestamp(datetime.datetime.now())
    }

    protected_string = _encode(json.dumps(protected_header))
    data_string = protected_string + b"." + _encode(payload)
    signatures = {
        "signatures": [{
            "header": {
                "jwk": {
                    "crv": "P-256",
                    "kid": _sign_key.kid,
                    "kty": "EC",
                    "x": _sign_key.x,
                    "y": _sign_key.y,
                },
                "alg": "ES256"
            },
            "signature": _encode(_sign_key.sign(data_string, hashfunc=sha256)).decode(),
            "protected": protected_string.decode()
        }]
    }
    signatures_string = json.dumps(signatures, indent=4)
    pretty_signatures_string = "\n".join(signatures_string.splitlines()[1:])
    return payload[:-2] + ",\n" + pretty_signatures_string


class Verifier(object):
    def __init__(self, content):
        self.content = content
        data = json.loads(content)
        self.signatures = data['signatures']
        self.payload = None

    def get_verify_key(self, header):
        if header['alg'] != "ES256":
            raise NotImplementedError()
        else:
            jwk = header['jwk']
            x = jwk['x']
            y = jwk['y']
            point_str = _decode(x) + _decode(y)
            vk = VerifyingKey.from_string(point_str, _crv_mapping[jwk['crv']], hashfunc=sha256)
            return vk

    def get_payload(self, protected_header):
        """
        获取 Response 的 Content，SHA256 校验用
        :param protected_header:
        :return:
        """
        if not self.payload:
            protected_data = json.loads(_decode(protected_header).decode())
            format_len = protected_data['formatLength']
            tail = _decode(protected_data['formatTail'])
            payload = self.content[:format_len] + tail.decode()
            self.payload = payload
        return self.payload

    def get_sign_bytes(self, protected_header):
        """
        获取 Payload JWS 签名校验用的
        :param protected_header:
        :return:
        """
        payload = self.get_payload(protected_header)
        payload_string = _encode(payload)

        message = protected_header.encode() + b"." + payload_string
        return message

    def verify(self):
        for signature in self.signatures:
            header = signature['header']
            protected_header = signature['protected']
            sign = signature['signature']
            payload = self.get_sign_bytes(protected_header)
            vk = self.get_verify_key(header)
            try:
                vk.verify(_decode(sign), payload)
            except BadSignatureError:
                return False

        return True
