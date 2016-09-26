from django.conf import settings
from django.test import TestCase, Client, override_settings

__author__ = 'pivstone'

@override_settings(REPO_DIR="test/v2/repo", BLOB_DIR="test/v2/blob")
class BlobsUploadTest(TestCase):
    """
    Blobs 上传的单元测试
    """

    def setUp(self):
        self.client = Client()
        self.data = b"hello"
        self.name = "test"
        self.uuid = "123"

    def _test_patch_blobs_upload(self):
        response = self.client.patch("/v2/test/blobs/uploads/123", data="hello", content_type="application/octet-stream",
                                    HTTP_RANGE="bytes=0-5")
        self.assertEqual(202, response.status_code)

        self.assertEqual("%s://%s/v2/test/blobs/uploads/%s" % (
            response.wsgi_request.scheme, response.wsgi_request.get_host(), self.uuid,),
                         response._headers['location'][1])

        self.assertEqual(self.uuid, response._headers['docker-upload-uuid'][1])

        file_name = "%s/%s/_uploads/%s" % (settings.REPO_DIR, self.name, self.uuid)
        with open(file_name, "rb") as f:
            self.assertEqual(self.data, f.read())
