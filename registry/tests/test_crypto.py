from django.test import TestCase
from .. import crypto

__author__ = 'pivstone'


class CryptoTest(TestCase):
    """
    JWS 加密相关测试
    """

    def setUp(self):
        pass

    def test_jws_sign(self):
        """
        测试 JWS 签发
        :return:
        """
        data = {"a": 1}
        signed = (crypto.jws_sign(data))
        vk = crypto.Verifier(content=signed)
        self.assertTrue(vk.verify())

    def test_jws_verify(self):
        """
        测试 JWS 验签
        :return:
        """
        with open("./registry/tests/data/schemaV1.json") as f:
            content = f.read()
            vk = crypto.Verifier(content=content)
            self.assertTrue(vk.verify())
