# coding=utf-8
import json

from django.conf import settings
from django.test import TestCase, override_settings
from registry.manifests import AbstractManifest, ManifestV1, ManifestV2

__author__ = 'pivstone'


@override_settings(
    BLOB_DIR="registry/tests/data/v2/blob"
)
class ManifestTestCase(TestCase):
    def setUp(self):
        """
        clear & prepare data
        :return:
        """

    def test_abstract_manifests_not_implements(self):
        """
        :CN 主要测试 AbstractManifest中抽象的方法，这些方法应该由子类实现
        :EN Test for abstract method in AbstractManifest class,those method shoud implemented by subclass
        :return:
        """
        with self.assertRaises(NotImplementedError):
            manifest = AbstractManifest("{}", {}, None, None)
            manifest.layers()
            manifest.verify()
            manifest.convert()

    def test_manifest_v1_verify(self):
        """
        :CN 测试 V1 版 Manifest 的Verify
        :EN test manifest v1 verify method
        :return:
        """
        print(settings.BLOB_DIR)
        with open("./registry/tests/data/schemaV1.json") as f:
            content = f.read()
            data = json.loads(content)
            manifest = ManifestV1(content, data, "my", "latest")

            self.assertTrue(manifest.verify())

    def test_manifest_v2_verify(self):
        """
        :CN 测试 V2 版 Manifest 的Verify
        :EN test manifest v2 verify method
        :return:
        """
        with open("./registry/tests/data/schemaV2.json") as f:
            content = f.read()
            data = json.loads(content)
            manifest = ManifestV2(content, data, "my", "latest")
            self.assertTrue(manifest.verify())

    def test_manifest_v2_convert(self):
        """
        :CN 测试 manifest v2 to v1 的转换
        :EN  test convert method for manifest v2 schema v2 to schema v1
        :return:
        """
        with open("./registry/tests/data/schemaV2.json") as f:
            content = f.read()
            data = json.loads(content)
            manifest = ManifestV2(content, data, "my", "latest")

            manifest_v1_string = manifest.convert()
            manifest_v1_data = json.loads(manifest_v1_string)
            manifest_v1 = ManifestV1(manifest_v1_string, manifest_v1_data, "my", "latest")
            self.assertTrue(manifest_v1.verify())
