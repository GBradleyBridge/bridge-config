import os
import unittest
from unittest.mock import MagicMock, patch

from bridgeconfig import bridgeconfig

os.environ["ENVIRONMENT"] = "ENV"
os.environ["SETTINGS_PATH"] = os.path.dirname(os.path.abspath(__file__))


class TestBridgeConfig(unittest.TestCase):
    def setUp(self):
        self.boto3_client_mock = patch("boto3.client")
        self.boto3_client = self.boto3_client_mock.start()
        self.ssm_client = MagicMock()
        self.boto3_client.return_value = self.ssm_client

        self.ssm_client.exceptions.ParameterNotFound = KeyError

        self.parameters = {
            "/PJT/ENV/K1": "V1",
            "/All/All/JSON": '{"some": "value"}',
            "/All/ENV/INT": "1",
            "/PJT/ENV/FALSE1": "false",
            "/PJT/ENV/FALSE2": "no",
            "/OTHER/Prod/Key": "Value",
        }

        def get_parameter(Name, WithDecryption=False, *args, **kwargs):
            value = self.parameters[Name]
            if not WithDecryption:
                value = "Still-Encrypted-Value"
            return {"Parameter": {"Name": Name, "Value": value, "Type": "SecureString"}}

        def get_parameters(Names, WithDecryption=False, *args, **kwargs):
            return {
                "Parameters": [
                    get_parameter(Name, WithDecryption)["Parameter"] for Name in Names
                ]
            }

        self.ssm_client.get_parameter.side_effect = get_parameter
        self.ssm_client.get_parameters.side_effect = get_parameters

        self.bc = bridgeconfig.BridgeConfig(project="PJT", environment="ENV")
        self.bc.get_raw_parameters = MagicMock()
        self.bc.get_raw_parameters.return_value = [
            {
                "Name": "/PJT/ENV/K1",
                "Value": "Still-Encrypted-Value",
                "Type": "SecureString",
            },
            {"Name": "/PJT/All/K2", "Value": "V2", "Type": "String"},
            {"Name": "/All/All/K3", "Value": "V3", "Type": "String"},
        ]

    def tearDown(self):
        self.boto3_client_mock.stop()

    def test_search_path(self):
        bc = bridgeconfig.BridgeConfig(project="PJT", environment="ENV")
        self.assertListEqual(
            bc.search_path, ["/All/All/", "/All/ENV/", "/PJT/All/", "/PJT/ENV/"]
        )

        bc = bridgeconfig.BridgeConfig(project="PJT", environment="All")
        self.assertListEqual(bc.search_path, ["/All/All/", "/PJT/All/"])

        bc = bridgeconfig.BridgeConfig(project="All", environment="All")
        self.assertListEqual(bc.search_path, ["/All/All/"])

    def test_get_param_name(self):
        self.assertEquals(self.bc.get_param_name("/PJT/ENV/KEY"), "KEY")
        self.assertEquals(self.bc.get_param_name("PJT/ENV/KEY"), "KEY")
        self.assertEquals(self.bc.get_param_name("/ENV/KEY"), "KEY")
        self.assertEquals(self.bc.get_param_name("ENV/KEY"), "KEY")

    def test_parameter_sarch_path(self):
        search_path = list(self.bc.parameter_sarch_path("KEY"))
        self.assertEquals(
            search_path,
            ["/PJT/ENV/KEY", "/PJT/All/KEY", "/All/ENV/KEY", "/All/All/KEY"],
        )

        search_path = list(self.bc.parameter_sarch_path("FIXED_ENV/KEY"))
        self.assertEquals(
            search_path,
            ["/PJT/FIXED_ENV/KEY", "/All/FIXED_ENV/KEY"],
        )

        search_path = list(self.bc.parameter_sarch_path("/FIXED_ENV/KEY"))
        self.assertEquals(
            search_path,
            ["/PJT/FIXED_ENV/KEY", "/All/FIXED_ENV/KEY"],
        )

        search_path = list(self.bc.parameter_sarch_path("FIXED_PJT/FIXED_ENV/KEY"))
        self.assertEquals(
            search_path,
            ["/FIXED_PJT/FIXED_ENV/KEY"],
        )

        search_path = list(self.bc.parameter_sarch_path("/FIXED_PJT/FIXED_ENV/KEY"))
        self.assertEquals(
            search_path,
            ["/FIXED_PJT/FIXED_ENV/KEY"],
        )

    def test_cache(self):
        self.assertEquals(
            self.bc.names,
            {"K1": "/PJT/ENV/K1", "K2": "/PJT/All/K2", "K3": "/All/All/K3"},
        )

        self.assertEquals(self.bc.still_encrypted, {"K1": "/PJT/ENV/K1"})

    def test_decrypt_parameters(self):
        self.bc.decrypt_parameters()
        self.ssm_client.get_parameters.assert_called_with(
            Names=["/PJT/ENV/K1"], WithDecryption=True
        )

        self.assertTrue(self.bc.lookup["/PJT/ENV/K1"].get("Decrypted"))

    def test_get_all_parameters(self):
        parameters = self.bc.get_all_parameters(decrypt=True)
        self.assertListEqual(
            parameters,
            [
                {"name": "/PJT/ENV/K1", "value": "V1"},
                {"name": "/PJT/All/K2", "value": "V2"},
                {"name": "/All/All/K3", "value": "V3"},
            ],
        )

    def test_get_parameter(self):
        self.assertEquals(
            self.bc.get_parameter("K1", decrypt=False), "Still-Encrypted-Value"
        )
        self.assertEquals(self.bc.get_parameter("K1", decrypt=True), "V1")
        self.assertEquals(self.bc.get_parameter("ENV/K1", decrypt=True), "V1")
        self.assertEquals(self.bc.get_parameter("PJT/ENV/K1", decrypt=True), "V1")
        self.assertEquals(self.bc.get_parameter("/PJT/ENV/K1", decrypt=True), "V1")

        self.assertEquals(self.bc.get_parameter("K2", decrypt=True), "V2")

        with self.assertRaises(bridgeconfig.ParameterNotFound):
            self.bc.get_parameter("NO_NO", decrypt=True)
        self.assertIsNone(self.bc.get_parameter("NO_NO", decrypt=True, default=None))

        self.assertEquals(
            self.bc.get_parameter("JSON", decrypt=True, type="json"), {"some": "value"}
        )

        self.assertEquals(self.bc.get_parameter("INT", decrypt=True, type="int"), 1)
        self.assertFalse(self.bc.get_parameter("FALSE1", decrypt=True, type="bool"))
        self.assertFalse(self.bc.get_parameter("FALSE2", decrypt=True, type="bool"))

    def test_conf(self):
        from bridgeconfig.conf import aws_formatter, settings

        with patch.object(aws_formatter, "bridge_config", self.bc):
            self.assertEquals(settings.APP_NAME, "PJT")
            self.assertEquals(settings.ENV, "ENV")
            self.assertEquals(settings.K2, "V2")
            self.assertEquals(settings.K1, "V1")
            self.assertEquals(settings["K1"], "V1")
            self.assertEquals(settings["FULLPATH_KEY"], "Value")
            data_file = os.path.join(os.path.dirname(__file__), 'test_data.txt')
            with open(data_file) as f:
                expected = f.read()
            self.assertEquals(settings["READFILE_KEY"], expected)
