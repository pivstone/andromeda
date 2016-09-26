from django.test import TestCase, Client

__author__ = 'pivstone'


class UrlsRouterTest(TestCase):
    """
    测试 URL Router的匹配情况
    """

    def setUp(self):
        self.client = Client()
        self.urls_list = [
            "/v2/",
            "/v2/_catalog",
        ]

    def test_v2_api_root(self):
        for url in self.urls_list:
            self.assertEqual(200, self.client.get(url).status_code)

    def test_docker_api_resolver(self):
        """
        检查Docker API 的 URLs
        :return:
        """
        from django.core.urlresolvers import resolve
        self.assertEqual(resolve("/v2/my/my/tags/list").view_name, 'registry.views.Tags')
        self.assertEqual(resolve("/v2/").view_name, 'registry.views.Root')
        self.assertEqual(resolve("/v2/_catalog").view_name, 'registry.views.Catalog')
        self.assertEqual(resolve("/v2/my/my/manifests/latest").view_name, 'registry.views.Manifests')
        self.assertEqual(resolve(
            "/v2/my/my/blobs/sha256:802d2a9c64e8f556e510b4fe6c5378b9d49d8335a766d156ef21c7aeac64c9d6").view_name,
                         'registry.views.Blobs')
