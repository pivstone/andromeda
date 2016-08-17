from django.conf import settings
from django.http import Http404
from django.test import TestCase, override_settings
import os, shutil
from registry.storages import storage

__author__ = 'pivstone'


@override_settings(REPO_DIR="test/v2/repo", BLOB_DIR="test/v2/blob")
class StorageTestCase(TestCase):
    def setUp(self):
        self.repo_name = "my2"
        self.tag_name = "1.2"
        if os.path.exists(settings.REPO_DIR):
            shutil.rmtree(settings.REPO_DIR)
        if os.path.exists(settings.BLOB_DIR):
            shutil.rmtree(settings.BLOB_DIR)

    def tearDown(self):
        if os.path.exists(settings.REPO_DIR):
            shutil.rmtree(settings.REPO_DIR)

        if os.path.exists(settings.BLOB_DIR):
            shutil.rmtree(settings.BLOB_DIR)

    def test_get_repositories_empty(self):
        """
        测试没有测试数据下的catalog 返回
        :return:
        """
        self.assertEqual([], storage.get_repositories())  # 没有测试数据应该为空

    def test_get_repositories(self):
        """
        测试 catalog 查询
        :return:
        """
        dir_name = settings.REPO_DIR + "/%s/_layers" % self.repo_name
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        self.assertEqual([self.repo_name], storage.get_repositories())

    def test_get_repositories_not_existed_keyword(self):
        """
        测试 无效关键字下的 catalog 搜索返回
        :return:
        """
        keyword = "t"
        self.assertFalse(self.repo_name.find(keyword) > 0)
        self.assertEqual([], storage.get_repositories(keyword=keyword))

    def test_get_repositories_existed_keyword(self):
        """
        测试 有效关键字下的 catalog 搜索返回
        :return:
        """
        keyword = "m"
        self.assertFalse(self.repo_name.find(keyword) > 0)
        self.assertEqual([], storage.get_repositories(keyword=keyword))

    def test_get_tags_empty(self):
        """
        测试获取 repo 不存在的情况 下tags返回
        :return:
        """

        with self.assertRaises(Http404):  # 没有测试数据，应该报 404
            storage.get_tags(self.repo_name)

    def test_get_tags_no_tag(self):
        """
        测试空 Repo 下 tags 的返回
        :return:
        """
        tag_path = storage.path_spec.get_tag_path(self.repo_name)
        os.makedirs(tag_path)
        self.assertEqual([], storage.get_tags(self.repo_name))

    def test_get_tags(self):
        """
        测试 repo get tags 的返回
        :return:
        """
        tag_path = storage.path_spec.get_tag_path(self.repo_name)
        os.makedirs(tag_path + "/" + self.tag_name)
        self.assertEqual([self.tag_name], storage.get_tags(self.repo_name))
