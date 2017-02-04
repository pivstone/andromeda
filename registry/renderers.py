# coding=utf-8
from rest_framework.renderers import JSONRenderer

__author__ = 'pivstone'


class ManifestV1Renderer(JSONRenderer):
    """
    防止 docker 只传 Manifest Type 的请求，然后导致 416 发生
    """
    media_type = "application/vnd.docker.distribution.manifest.v1+prettyjws"


class ManifestV2Renderer(JSONRenderer):
    """
    防止 docker 只传 Manifest Type 的请求，然后导致 416 发生
    """
    media_type = "application/vnd.docker.distribution.manifest.v2+json"
