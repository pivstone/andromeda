import json
import logging

from django import http
from django.http import HttpResponse
from registry.decorators import digest_hash
from registry.parsers import ManifestV1Parser, ManifestV2Parser
from registry import exceptions
from registry.manifests import Manifest
from registry.storages import storage
from rest_framework.views import APIView

__author__ = 'pivstone'

LOG = logging.getLogger(__name__)


class Root(APIView):
    def get(self, request):
        """
        API Root View
        :param request:
        :return:
        """
        return http.JsonResponse(data=dict())


class Tags(APIView):
    scope = "repository"

    def get(self, request, name=None):
        """
        Tags List View
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        return http.JsonResponse(data={"name": name, "tags": storage.get_tags(name)})


class Manifests(APIView):
    scope = "repository"

    @digest_hash()
    def get(self, request, name=None, reference=None):
        """
        Manifests Views
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        content = storage.get_manifest(name, reference)
        if not content:
            raise http.Http404()
        accept_list = request.META.get("HTTP_ACCEPT", [])
        schema_v2 = True
        if ManifestV1Parser.media_type in accept_list and ManifestV2Parser.media_type not in accept_list:
            schema_v2 = False
        manifest = json.loads(content)
        if schema_v2:
            response = http.JsonResponse(data=manifest)
            response["content-Type"] = manifest['mediaType']
            return response
        else:
            mani = Manifest(manifest, name=name, reference=reference)
            response = http.HttpResponse(content=mani.get_v1_manifest())
            response["content-Type"] = ManifestV1Parser.media_type
            return response

    @digest_hash()
    def put(self, request, name=None, reference=None):
        """
        Create Manifests Views
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        schema = request.META.get("CONTENT_TYPE", None)
        if not schema:
            raise exceptions.RegistryException()
        if schema not in (ManifestV1Parser.media_type, ManifestV2Parser.media_type,):
            raise exceptions.UnsupportedException()
        manifest = Manifest(request.read(), name, reference)
        manifest.save()
        return http.JsonResponse(data={"name": name, "reference": reference})

    @digest_hash()
    def delete(self, request, name=None, reference=None):
        """
        Delete Manifests Views
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        return http.JsonResponse(data={"name": name, "reference": reference})


class Blobs(APIView):
    scope = "repository"

    def get(self, request, name=None, digest=None):
        """
        Blod Down Views
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        digest_method, digest_value = digest.split(":")
        return http.HttpResponseRedirect(
            "/download/blobs/%s/%s/%s/data" % (digest_method, digest_value[:2], digest_value))

    def delete(self, request, name=None, digest=None):
        """
        Blod Down Views
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        return http.JsonResponse(data={"name": name, "digest": digest})

    @digest_hash()
    def head(self, request, name=None, digest=None):
        """
        Blod Down Views
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        content_length = storage.get_blob_length(digest)
        if not content_length:
            raise http.Http404()
        response = http.HttpResponse()
        response["content-length"] = content_length
        return response


class BlobsUploadsInit(APIView):
    scope = "repository"

    def post(self, request, name=None):
        """
         /v2/<name>/blobs/uploads/
        开始上传 Blob 的准备
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """
        if len(name) > 256:
            raise exceptions.NameInvalidException()
        upload_id = storage.create_blob(name)
        status = 202
        if "mount" in request.GET:
            status = 201
        response = http.HttpResponse(status=status)
        response['Location'] = request.get_full_path() + upload_id
        response['Docker-Upload-UUID'] = upload_id
        response['Range'] = '0-0'
        return response


class BlobsUploads(APIView):
    scope = "repository"

    @digest_hash()
    def patch(self, request, name=None, uuid=None):
        """
        /v2/<name>/blobs/uploads/<uuid>
        Blob 上传
        :param request: Http 请求对象
        :param name: 镜像名
        :return:
        """

        length = storage.save_full_upload(request, name, uuid)
        response = HttpResponse(status=202)
        response['Range'] = "0-%s" % length
        response['Docker-Upload-UUID'] = uuid
        response['Location'] = request.get_full_path()
        return response

    @digest_hash()
    def put(self, request, name=None, uuid=None):
        client_digest = request.GET['digest']
        hash_method = client_digest.split(":")[0]
        file_digest = storage.get_blob_digest(name, uuid, hash_method)
        if client_digest != "sha256:" + file_digest:
            LOG.info("Digest Not Match,client_digest:%s,file_digest:%s" % (client_digest, file_digest))
            raise exceptions.BlobDigestInvalidException()
        storage.commit(name, uuid, client_digest)
        response = HttpResponse(status=204)
        response['Docker-Upload-UUID'] = uuid
        response['Location'] = request.get_full_path()
        return response

    def get(self, request, name=None, uuid=None):
        response = HttpResponse(status=204)
        response['Docker-Upload-UUID'] = uuid
        return response

    def post(self, request, name=None, uuid=None):
        response = HttpResponse(status=204)
        response['Docker-Upload-UUID'] = uuid
        response['Location'] = request.get_full_path()
        return response


class Catalog(APIView):
    scope = "registry"

    def get(self, request):
        """
        catalog view
        :param request: Http 请求对象
        :return:
        """
        q = request.GET.get("q", request.data.get("q", ""))
        n = request.GET.get("n", request.data.get("n", 10))
        try:
            n = int(n)
        except ValueError:
            n = 10
        repositories = storage.get_repositories(keyword=q, n=n)
        return http.JsonResponse(data={"repositories": repositories})
