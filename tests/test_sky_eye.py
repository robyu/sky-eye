from sky_eye import sky_eye
import unittest
from sky_eye import mqtt_topics
from pathlib import Path
from sky_eye import mqtt_if

class TestSkyEye(unittest.TestCase):
    def test_smoke(self):
        eye = sky_eye.SkyEye(Path("tests/test-config.json"))
        self.assertTrue(True)

    def test_take_image(self):
        import pudb; pudb.set_trace()
        eye = sky_eye.SkyEye(Path("tests/test-config.json"))
        msg = mqtt_if.new_msg(mqtt_topics.MqttTopics.SKY_EYE_CAPTURE_NOW, "test.jpg")
        eye._run_once(msg)
        self.assertTrue(True)


