import paho.mqtt.client as mqtt
import sys
import time
import os
import uuid
from dataclasses import dataclass
from queue import Queue
import logging
from sky_eye import mqtt_topics


"""
Paho General flow:
    Create a client instance
    Connect to a broker using one of the connect*() functions
    Call one of the loop*() functions to maintain network traffic flow with the broker
    Use subscribe() to subscribe to a topic and receive messages
    Use publish() to publish messages to the broker
    Use disconnect() to disconnect from the broker
"""
def new_msg(topic, payload):
    # msg = mqtt.MQTTMessage(topic=str(topic).encode('utf-8'))
    # msg.payload = str(payload).encode('utf-8')
    if isinstance(topic, bytes)==False:
        topic = topic.encode('utf-8')
    #
    if isinstance(payload, bytes)==False:
        payload = payload.encode('utf-8')
    #
    msg = mqtt.MQTTMessage(topic=topic)
    msg.payload = payload
    return msg
        
class MqttIf:
    MAX_QUEUE_LEN = 100

    def __init__(self, broker_addr, listen_topics_l = [], test_client=None):
        #import pudb;pudb.set_trace()
        client_id = "mqtt-client-" + str(uuid.uuid4())
        
        # https://pypi.org/project/paho-mqtt/
        # userdata = passed to callbacks as "userdata" parameter
        if test_client == None:
            self.client =mqtt.Client(client_id=client_id, userdata=self)
        else:
            self.client = test_client(client_id=client_id, userdata=self)

        self.broker_addr = broker_addr
        self.client.on_message = MqttIf.on_message
        self.client.on_connect = MqttIf.on_connect
        
        logger = logging.getLogger()
        self.client.enable_logger(logger)

        self.listen_topics_l = listen_topics_l

        """
        maxsize – Number of items allowed in the queue.
        empty() – Return True if the queue is empty, False otherwise.
        full() – Return True if there are maxsize items in the queue. If the queue was initialized with maxsize=0 (the default), then full() never returns True.
        get() – Remove and return an item from the queue. If queue is empty, wait until an item is available.
        get_nowait() – Return an item if one is immediately available, else raise QueueEmpty.
        put(item) – Put an item into the queue. If the queue is full, wait until a free slot is available before adding the item.
        put_nowait(item) – Put an item into the queue without blocking. If no free slot is immediately available, raise QueueFull.
        qsize() – Return the number of items in the queue.                               
        """
        self.msg_queue = Queue(self.MAX_QUEUE_LEN)

        return

    def reconnect(self):
        """
        reconnect with broker

        this function loops until the connection occurs
        if it returns False, then the connection failed
        """
        if self.client.is_connected():
            self.client.disconnect()
        #
        self.client.connect(self.broker_addr, port=1883, keepalive=60)

        for topic in self.listen_topics_l:
            self.client.subscribe(topic)
        #

        # loop until we're connected
        count = 1000
        while self.client.is_connected()==False:
            self.loop()
            count = count - 1

            assert count >= 0, "mqtt_if.reconnect took too long"
        #
        return self.client.is_connected()
        

    def on_connect(mqttc, obj, flags, rc):
        # obj = 2nd argument to Client() ctor
        logging.info("connected: " + str(rc))

    def on_message(client, userdata, message):
        #import pudb; pudb.set_trace()
        myself = userdata
        assert myself.msg_queue.full() == False
        myself.msg_queue.put(message)
        logging.info("Received message '" + message.payload.decode('utf-8') + "' on topic '"
              + message.topic)
        logging.info(f"msg queue has {myself.msg_queue.qsize()} messages")
        
    def queue_is_empty(self):
        return self.msg_queue.empty()
        
    def get_len_queue(self):
        return self.msg_queue.qsize()

    def loop(self):
        self.client.loop(timeout=0.25)  # default timeout is 1.0 s, too long
        return

    def queue_msg(self, message):
        self.msg_queue.put(message)

    def dequeue_msg(self):
        msg = self.msg_queue.get(block=False)   # block=False -> raise exception if empty
        return msg

    def dequeue_msg_str(self):
        """
        return dequeued message, but convert payload to utf-8 string
        """
        msg = self.msg_queue.get(block=False)   # block=False -> raise exception if empty
        msg.payload = msg.payload.decode("utf-8")
        return msg
    
    
