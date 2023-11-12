from sky_eye import sky_eye
import unittest
from sky_eye import mqtt_topics
from pathlib import Path
from sky_eye import mqtt_if
from sky_eye import config_store
import shutil
import datetime as dt
import time

class TestSkyEye(unittest.TestCase):
    #import pudb; pudb.set_trace()

    TEST_CONFIG_FILE=Path("tests/test-config.json").absolute()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # code to run only once during initialization
        self.config = config_store.ConfigStore(self.TEST_CONFIG_FILE)
        self.ftp_dest_dir = Path(self.config.ftp_dest_dir).absolute()
        assert self.ftp_dest_dir.exists()   


    def setUp(self):
        # Delete all files in FTP_DEST_DIR directory
        shutil.rmtree(self.ftp_dest_dir, ignore_errors=True)
        self.ftp_dest_dir.mkdir(parents=True, exist_ok=True)
    
    def test_smoke(self):
        eye = sky_eye.SkyEye(self.TEST_CONFIG_FILE)
        self.assertTrue(True)

    def test_take_image(self):

        eye = sky_eye.SkyEye(self.TEST_CONFIG_FILE)
        msg = mqtt_if.new_msg(mqtt_topics.MqttTopics.SKY_EYE_CAPTURE_NOW, "test.jpg")
        eye._run_once(msg)

        # check that a file ended up in self.ftp_dest_dir
        dest_file = self.ftp_dest_dir / "test.jpg"
        self.assertTrue(dest_file.exists())


    def test_connect_broker(self):
        #import pudb; pudb.set_trace()
        test_mqtt = mqtt_if.MqttIf(self.config.mqtt_broker_addr, 
                                   client_id = "test_connect_broker",
                                   listen_topics_l=[mqtt_topics.MqttTopics.SKY_EYE_TOPIC + "/#"])
        is_connected=test_mqtt.reconnect()
        self.assertTrue(is_connected)

        eye = sky_eye.SkyEye(self.TEST_CONFIG_FILE)
        # add im_alive_sec to now
        now_dt = dt.datetime.now() + dt.timedelta(seconds=eye.im_alive_sec)
        eye._do_loop_tasks(now=now_dt)

        # skyeye should have published "connected" and "imalive"
        time.sleep(0.5)  # give messages time to bounce around
        num_rcvd = test_mqtt.get_len_queue()
        self.assertTrue(num_rcvd == 2)

        topic_set = [mqtt_topics.MqttTopics.SKY_EYE_CONNECTED, 
                     mqtt_topics.MqttTopics.SKY_EYE_IM_ALIVE]
        msg = test_mqtt.dequeue_msg()
        self.assertTrue(msg.topic in topic_set)

        msg = test_mqtt.dequeue_msg()
        self.assertTrue(msg.topic in topic_set)




    