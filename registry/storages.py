# coding=utf-8
import logging
from django.utils import six
from importlib import import_module
from registry import exceptions, signals
from django import http
from django.conf import settings
import hashlib
import os
from registry.utils import ensure_dir

__author__ = 'pivstone'

LOG = logging.getLogger(__name__)


class FileSystemPathSpec(object):
    """
   Docker Registry 的文件存储结构
   ref:[https://github.com/docker/distribution/blob/641f1029677e49faa277f7769797518e973865fd/registry/storage/paths.go#L24]
   The path layout in the storage backend is roughly as follows:

           <root>/v2
               -> repositories/
                   -><name>/
                       -> _manifests/
                           revisions
                               -> <manifest digest path>
                                   -> link
                           tags/<tag>
                               -> current/link
                               -> index
                                   -> <algorithm>/<hex digest>/link
                       -> _layers/
                           <layer links to blob store>
                       -> _uploads/<id>
                           data
                           startedat        # 上传文件的时间而已，个人觉得改成 Info 更合适一些
                           hashstates/<algorithm>/<offset>
               -> blob/<algorithm>
                   <split directory content addressable storage>
   """

    def get_upload_info_path(self, name, uuid):
        """
        上传文件的信息
        :param name: 镜像名 UUID
        :param uuid:
        :return:
        """
        return "%s/%s/_uploads/%s/info" % (settings.REPO_DIR, name, uuid)

    def get_upload_path(self, name, uuid):
        """
        上传文件的临时路径
        :param name:
        :param uuid:
        :return:
        """
        return "%s/%s/_uploads/%s/data" % (settings.REPO_DIR, name, uuid)

    def get_blob_path(self, digest):
        """
        上传完成后的 blob 路径
        :param digest:
        :return:
        """
        hash_method, digest_value = digest.split(":")
        return "%s/%s/%s/%s/data" % (settings.BLOB_DIR, hash_method, digest_value[:2], digest_value)

    def get_tag_path(self, name):
        return "%s/%s/_manifests/tags" % (settings.REPO_DIR, name)

    def get_tag_current_path(self, name, tag_name):
        return "%s/%s/_manifests/tags/%s/current" % (settings.REPO_DIR, name, tag_name)

    def get_tag_index_path(self, name, tag_name, digest):
        hash_method, hash_value = digest.split(":")
        return "%s/%s/_manifests/tags/%s/index/%s/%s" % (settings.REPO_DIR, name, tag_name, hash_method, hash_value)

    def get_reference_path(self, name, digest):
        hash_method, hash_value = digest.split(":")
        return "%s/%s/_manifests/revisions/%s/%s" % (settings.REPO_DIR, name, hash_method, hash_value)

    def get_layer_path(self, name, digest):
        """
        获取 Layers 存储路径
        :param name:
        :return:
        """
        hash_method, hash_value = digest.split(":")
        return "%s/%s/_layers/%s/%s" % (settings.REPO_DIR, name, hash_method, hash_value)


class FileSystemStorage(object):
    """
    File based Storage
    """

    def __init__(self):
        self.path_spec = FileSystemPathSpec()

    def __getattr__(self, item):
        return getattr(self.path_spec, item)

    def get_blob(self, digest):
        """
        获取 blob 内容
        :param digest:
        :return:
        """
        file_name = self.path_spec.get_blob_path(digest)
        if not os.path.exists(file_name):
            raise http.Http404()
        with open(file_name, "r") as f:
            return f.read()

    def get_repositories(self, n=10, keyword=""):
        found_path = []
        for root, sub, f in os.walk(settings.REPO_DIR):
            if "_layers" in sub:
                if keyword:
                    if root.find(keyword) > 0:
                        found_path.append(root.replace(settings.REPO_DIR + "/", ""))
                else:
                    found_path.append(root.replace(settings.REPO_DIR + "/", ""))
            if len(found_path) >= n:
                break
        return found_path

    def get_tags(self, name):
        """
        获取 Repo 下所有的tags
        :param name:
        :return:
        """
        tag_path = self.path_spec.get_tag_path(name)
        found_tags = []
        if not os.path.exists(tag_path):
            raise http.Http404()
        for f in os.listdir(tag_path):
            f_path = os.path.join(tag_path, f)
            if os.path.exists(f_path) and not os.path.isfile(f_path):
                found_tags.append(f)
        return found_tags

    def get_manifest(self, name, reference):
        """
        获取 Manifest 内容
        :param name:
        :param reference:
        :return:
        """
        if reference.startswith("sha256:"):
            digest = reference
            if not self.get_blob_length(digest):
                raise exceptions.ManifestUnknownException(
                    detail={"Path": self.path_spec.get_tag_current_path(name, reference), "DriverName": "filesystem"})
        else:
            tag_current_path = self.path_spec.get_tag_current_path(name, reference)
            tag_current_path += "/link"
            if not os.path.exists(tag_current_path):
                LOG.warn("path %s not found:" % tag_current_path)
                raise exceptions.ManifestUnknownException(detail={"Tags": reference})
            with open(tag_current_path, "r") as f:
                digest = f.read()
        return self.get_blob(digest)

    def create_blob(self, name):
        """
        :CN 创建上传文件的blob
        :EN create upload temp blob
        :param name:
        :return:
        """
        import uuid
        upload_id = uuid.uuid4().__str__()
        file_name = self.path_spec.get_upload_path(name, upload_id)
        ensure_dir(file_name)
        signals.blob_upload_init.send(sender=self.__class__, name=name, uuid=upload_id)
        return upload_id

    def save_full_upload(self, request, name, uuid):
        """
        完整存储上传文件
        :param request:
        :return:
        """
        file_name = self.path_spec.get_upload_path(name, uuid)
        dir_name = os.path.dirname(file_name)
        if not os.path.exists(dir_name):
            raise exceptions.BlobUploadUnknownException()
        content_length = request.META.get("CONTENT_LENGTH", 0)
        try:
            content_length = int(content_length)
        except ValueError:
            content_length = 0

        if content_length:
            with open(file_name, "w+b") as f:
                for chunk in iter(request.read, 16 * 1024):
                    if not chunk:
                        break
                    f.write(chunk)
                    f.flush()

        return os.stat(file_name).st_size if content_length else 0

    def get_blob_digest(self, name, uuid, hash_method="sha256"):
        """
        计算 Blob 的 Digest值
        :param name:
        :param uuid:
        :param hash_method:
        :return:
        """
        hash_func = {"sha256": hashlib.sha256, "sha1": hashlib.sha1}[hash_method]()
        file_name = self.path_spec.get_upload_path(name, uuid)
        if not os.path.exists(file_name):
            raise http.Http404()
        with open(file_name, "rb") as f2:
            for chunk in iter(lambda: f2.read(4096), b''):
                hash_func.update(chunk)
        return hash_func.hexdigest()

    def check_digest(self, digest):
        """
        :CN 检测 Blob的 digest 值
        :EN check blob file's digest value
        :param digest:
        :return:
        """
        hash_method, digest_value = digest.split(":")
        hash_func = {"sha256": hashlib.sha256, "sha1": hashlib.sha1}[hash_method]()
        file_name = self.path_spec.get_blob_path(digest)
        with open(file_name, "rb") as f2:
            for chunk in iter(lambda: f2.read(4096), b''):
                hash_func.update(chunk)
        return digest_value == hash_func.hexdigest().lower()

    def commit(self, name, uuid, digest):
        """
        持久化 Blob 对象

        将 _upload 文件夹中 move 到 blob 中
        :param name:
        :param uuid:
        :param digest:
        :return:
        """
        file_name = self.path_spec.get_upload_path(name, uuid)
        target_name = self.path_spec.get_blob_path(digest)
        ensure_dir(target_name)
        os.rename(file_name, target_name)
        signals.blob_upload_complete.send(sender=self.__class__, name=name, uuid=uuid, digest=digest)

    def get_blob_length(self, digest):
        file_name = self.path_spec.get_blob_path(digest)
        try:
            return os.stat(file_name).st_size
        except OSError:
            return None

    def save_manifest(self, data):
        """
        保存 Manifest 内容
        :param data:
        :return:
        """
        hash_fn = hashlib.sha256()
        hash_fn.update(data)
        digest = "sha256:" + hash_fn.hexdigest()
        target_name = self.path_spec.get_blob_path(digest)
        ensure_dir(target_name)
        with open(target_name, "w+b") as f:
            f.write(data)
        return digest

    def link(self, digest, target_name):
        """
        Link Blob 到指定目录
        :param digest: sha256：XXX 格式的
        :param target:
        :return:
        """
        target_name += "/link"
        if not isinstance(digest, six.binary_type):
            digest = digest.encode("utf-8")
        ensure_dir(target_name)
        with open(target_name, "w+b")as f:
            f.write(digest)


if hasattr(settings, "STORAGE"):
    try:
        storage = import_module(settings.STORAGE)
    except ImportError:
        storage = FileSystemStorage()
else:
    storage = FileSystemStorage()
