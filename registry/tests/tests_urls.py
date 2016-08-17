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
