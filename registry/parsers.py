from rest_framework.parsers import JSONParser

__author__ = 'pivstone'


class ManifestV2Parser(JSONParser):
    """
    Docker Manifest Schema V2_2
    """
    media_type = "application/vnd.docker.distribution.manifest.v2+json"


class ManifestV1Parser(JSONParser):
    """
    Docker Manifest Schema V2_1
    """
    media_type = "application/vnd.docker.distribution.manifest.v1+prettyjws"
