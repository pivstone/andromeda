from django.conf import settings
from django.test import TestCase, Client, override_settings
import os
from registry.storages import storage

__author__ = 'pivstone'


class BlobsUploadTest(TestCase):
    """
    Blobs 上传的单元测试
    """

    def setUp(self):
        self.client = Client()
        self.data = b"hello"
        self.name = "my"
        self.uuid = "123"
        self.reference = "latest"

    @override_settings(BLOB_DIR="registry/tests/data/v2/blob", REPO_DIR="registry/tests/data/v2/repo")
    def test_get_manifest(self):
        """
        测试 GET manifest method
        :return:
        """
        response = self.client.get("/v2/%s/manifests/%s" % (self.name, self.reference),
                                   HTTP_ACCEPT="application/vnd.docker.distribution.manifest.v1+prettyjws")
        self.assertEqual(response.status_code, 200)
        content = storage.get_manifest(self.name, self.reference)

        self.assertEqual(content, response.content.decode("utf-8"))

    @override_settings(REPO_DIR="test/v2/repo", BLOB_DIR="test/v2/blob")
    def test_init_blobs_upload(self):
        """
        blob upload init 的post views 的测试
        :return:
        """
        response = self.client.post("/v2/%s/blobs/uploads/" % self.name, data="",
                                    content_type="application/octet-stream",
                                    HTTP_RANGE="bytes=0-0")
        self.assertEqual(202, response.status_code)
        upload_uuid = response._headers['docker-upload-uuid'][1]
        file_name = storage.path_spec.get_upload_path(self.name, upload_uuid)
        # todo: change to storage method
        dir_name = os.path.dirname(file_name)
        self.assertTrue(os.path.exists(dir_name))

    @override_settings(REPO_DIR="test/v2/repo", BLOB_DIR="test/v2/blob")
    def test_patch_blobs_upload(self):
        """
        :CN 测试 Blobs 的 Patch 上传
        :EN test blob upload though 'PATCH' method
        :return:
        """
        upload_id = storage.create_blob(self.name)

        response = self.client.patch("/v2/%s/blobs/uploads/%s" % (self.name, upload_id), data="hello",
                                     content_type="application/octet-stream",
                                     HTTP_RANGE="bytes=0-5")
        self.assertEqual(202, response.status_code)

        self.assertEqual("/v2/%s/blobs/uploads/%s" % (self.name, upload_id,),
                         response._headers['location'][1])

        self.assertEqual(upload_id, response._headers['docker-upload-uuid'][1])

        file_name = "%s/%s/_uploads/%s/data" % (settings.REPO_DIR, self.name, upload_id)
        with open(file_name, "rb") as f:
            self.assertEqual(self.data, f.read())
