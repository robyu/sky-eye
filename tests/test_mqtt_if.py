from stove_imagecap import mqtt_if
import unittest
from unittest.mock import MagicMock
from stove_imagecap import mqtt_topics

class TestMqttIf(unittest.TestCase):
    def test_smoke(self):
        rcvr = mqtt_if.MqttIf("localhost")
        self.assertTrue(True)

    def test_smoke_with_mock(self):
        mock_client = MagicMock()
        rcvr = mqtt_if.MqttIf("localhost", test_client=mock_client)
        self.assertTrue(True)

    def test_connecte_with_mock_mqtt(self):
            mock_client = MagicMock()
            rcvr = mqtt_if.MqttIf("localhost", test_client=mock_client)
            rcvr.reconnect()
            self.assertTrue(rcvr.client.subscribe.call_args[0][0]==mqtt_topics.MqttTopics.STOVE_IMAGECAP_TOPIC + "/#")
            self.assertTrue(True)

