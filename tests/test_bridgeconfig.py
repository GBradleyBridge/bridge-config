import unittest

from bridgeconfig import bridgeconfig


class TestBridgeConfig(unittest.TestCase):

    def setUp(self):
        self.BC = bridgeconfig.BridgeConfig(
            project="test", environment="develop"
        )

    def test_get_full_path(self):
        fullpath = self.BC.get_full_path(path="debug")
        self.assertEqual("/test/develop/debug", fullpath)

        fullpath = self.BC.get_full_path(path="debug/a/b")
        self.assertEqual("/test/develop/debug/a/b", fullpath)

        fullpath = self.BC.get_full_path(path="debug/a/b/c/d")
        self.assertEqual("/test/develop/debug/a/b/c/d", fullpath)
