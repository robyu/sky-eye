from sky_eye import mqtt_if
import unittest
from unittest.mock import MagicMock
from sky_eye import mqtt_topics

class TestMqttIf(unittest.TestCase):
    def test_smoke(self):
        rcvr = mqtt_if.MqttIf("localhost", listen_topics_l=[mqtt_topics.MqttTopics.SKY_EYE_TOPIC + "/#"])
        self.assertTrue(True)

    def test_smoke_with_mock(self):
        mock_client = MagicMock()
        rcvr = mqtt_if.MqttIf("localhost", test_client=mock_client, listen_topics_l=[mqtt_topics.MqttTopics.SKY_EYE_TOPIC + "/#"])
        self.assertTrue(True)

    def test_connect_with_mock_mqtt(self):
            #import pudb; pudb.set_trace()
            mock_client = MagicMock()
            rcvr = mqtt_if.MqttIf("localhost", test_client=mock_client, listen_topics_l=[mqtt_topics.MqttTopics.SKY_EYE_TOPIC + "/#"])
            rcvr.reconnect()
            self.assertTrue(rcvr.client.subscribe.call_args[0][0]==mqtt_topics.MqttTopics.SKY_EYE_TOPIC + "/#")
            self.assertTrue(True)

