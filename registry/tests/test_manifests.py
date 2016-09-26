import json
import shutil
from django.conf import settings
from django.test import TestCase
import os
from registry.manifests import AbstractManifest, ManifestV1

__author__ = 'pivstone'


class ManifestTestCase(TestCase):
    def setUp(self):
        """
        clear & prepare data
        :return:
        """
        if os.path.exists(settings.REPO_DIR):
            shutil.rmtree(settings.REPO_DIR)

        if os.path.exists(settings.BLOB_DIR):
            shutil.rmtree(settings.BLOB_DIR)

        from registry.storages import storage

        def create_digest(self, digest):
            target_name = self.path_spec.get_blob_path(digest)
            dir_name = os.path.dirname(target_name)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(target_name, "a") as f:
                f.write("null")

        storage.create_digest = create_digest
        self.storage = storage

    def test_abstract_manifests_not_implements(self):
        """
        :CN 主要测试 AbstractManifest中抽象的方法，这些方法应该由子类实现
        :EN Test for abstract method in AbstractManifest class,those method shoud implemented by subclass
        :return:
        """
        with self.assertRaises(NotImplementedError):
            manifest = AbstractManifest("{}", None, None)
            manifest.layers()
            manifest.verify()
            manifest.convert()

    def test_manifest_v1_verify(self):
        with open("./registry/tests/data/schemaV1.json") as f:
            content = f.read()
            data = json.loads(content)
            for layer in data['fsLayers']:
                self.storage.create_digest(self.storage, layer['blobSum'])
            manifest = ManifestV1(content, "my", "latest")

            self.assertTrue(manifest.verify())

    def tearDown(self):
        """
        clean data
        :return:
        """
        if os.path.exists(settings.REPO_DIR):
            shutil.rmtree(settings.REPO_DIR)

        if os.path.exists(settings.BLOB_DIR):
            shutil.rmtree(settings.BLOB_DIR)
