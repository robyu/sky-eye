import cv2
import argparse
import sys
from pathlib import Path
from . import config_store
from . import mqtt_if
from . import mqtt_topics
import ftplib
import datetime as dt
import time
from pathlib import Path
import logging

class SkyEye:

    def _check_cam_params(self):
        assert self.camera_index >= 0, f"camera index must be > 0"
        
        # try to open the camera
        cap = cv2.VideoCapture(self.camera_index)
        assert cap.isOpened(), f"could not open camera {self.camera_index}"
        ret, frame = cap.read()
        assert ret==True
        assert len(frame.shape) == 3
        cap.release()

    def _prep_image_dir(self, image_dir):
        if not image_dir.exists():
            image_dir.mkdir()
        #
        # delete all files in image_dir
        for f in image_dir.glob("*"):
            f.unlink()


        
    def __init__(self, config_fname):
        config = config_store.ConfigStore(config_fname)

        self.camera_index = config.camera_index
        self._check_cam_params()

        self.mqtt_broker_addr = config.mqtt_broker_addr

        self.image_dir = Path(config.image_dir).absolute()
        self.ftp_server_addr = config.ftp_server_addr
        self.ftp_server_port = config.ftp_server_port
        self.ftp_user = config.ftp_user
        self.ftp_passwd = config.ftp_passwd
        self._prep_image_dir(self.image_dir)
        self.mqtt_topics_l = [mqtt_topics.MqttTopics.SKY_EYE_CAPTURE_NOW,
                              mqtt_topics.MqttTopics.SKY_EYE_RESET_IMAGE_CAPTURE]
        
        self.mqtt = mqtt_if.MqttIf(self.mqtt_broker_addr,
                                   listen_topics_l = self.mqtt_topics_l)

        self.last_reconnect_time = dt.datetime.now()
        self.reconnect_sec = 10.0 * 60.0
        self.last_im_alive_time = dt.datetime.now()
        self.im_alive_sec = 15.0 * 60.0

        # DEBUG, INFO, WARNING, ERROR, CRITICAL
        self._configure_logging("DEBUG")

    # BEGIN: yz18jx9d4h3k
    @staticmethod
    def grab_camera_frame(camera_index):
        cap = cv2.VideoCapture(camera_index)

        # Check if the camera is opened successfully
        if not cap.isOpened():
            print("Unable to open the camera")
            return None

        # Read the frame from the camera
        ret, frame = cap.read()

        # Check if the frame was successfully read
        if not ret or len(frame.shape) != 3:
            print(f"Failed to capture frame from the camera {camera_index}")
            return None

        # Release the camera
        cap.release()

        return frame

    def _configure_logging(self, loglevel):
        """
        """
        try:
            numeric_level = getattr(logging, loglevel.upper(), None)
        except:
            assert False, f"{loglevel} is not a valid loglevel"
        #

        logging.basicConfig(stream=sys.stdout,
                            level=numeric_level,
                            format='%(asctime)s %(levelname)-8s %(message)s')
 
        logging.debug(   "DEBUG     logging enabled")
        logging.info(    "INFO      logging enabled")
        logging.warning( "WARNING   logging enabled")
        logging.error(   "ERROR     logging enabled")
        logging.critical("CRITICAL logging enabled")

    def _capture_image(self, out_fname):
        frame = self.grab_camera_frame(self.camera_index)
        
        # Save the captured image to a file
        cv2.imwrite(str(out_fname), frame)
        print(f"wrote file to {out_fname}")



    def _do_loop_tasks(self, now_dt = None):
        """                                                                                                                                                               
        1. establish/reconnect with server                                                                                                                                
        2. publish "i'm alive"                                                                                                                                            
        """
        if now_dt==None:
            now_dt = dt.datetime.now()
        else:
            assert isinstance(now_dt, dt.datetime)
        #
        delta = now_dt - self.last_reconnect_time
        assert delta.total_seconds() >= 0.0

        # periodically reconnect with server.
        # this solves the issue where if the server reboots, the mqtt server 
        # does not reestablish connections with the clients nor does the client  
        # know that the server has disappeared.                                                                                                                           
        if self.mqtt.client.is_connected()==False or delta.total_seconds() >= self.reconnect_sec:
            self.mqtt.reconnect()  # blocks: does not return until connection reestablished
            logging.info(f"Reconnected to server {self.mqtt.broker_addr} @ {now_dt}, delta_sec={delta.total_seconds():.2f}, interval_sec={self.reconnect_sec:.2f}" )
            self.mqtt.client.publish(mqtt_topics.MqttTopics.SKY_EYE_CONNECTED , payload=f"{now_dt}")
            self.last_reconnect_time = dt.datetime.now()
        #                                                                                                                                                                 

        delta = now_dt - self.last_im_alive_time
        assert delta.total_seconds() >= 0.0
        if delta.total_seconds() >= self.im_alive_sec:
            logging.info(f"I'm alive @ {now_dt}, delta_sec={delta.total_seconds():.2f}, interval_sec={self.im_alive_sec:.2f}")
            self.mqtt.client.publish(mqtt_topics.MqttTopics.SKY_EYE_IM_ALIVE, payload=f"{now_dt}")
            self.last_im_alive_time = dt.datetime.now()
        #                                                                                                                                                               
        return
    
    def _handle_msg(self, msg):
        quit_flag = False

        if msg.topic==mqtt_topics.MqttTopics.SKY_EYE_CAPTURE_NOW:
            print("handling capture_now")
            # if msg argument is "", then generate a filename based on the time-date
            if msg.payload=="":
                out_fname = self.image_dir / f"{dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            else:
                out_fname = self.image_dir / Path(msg.payload.decode('utf-8'))
            #
            out_fname = out_fname.absolute()

            self._capture_image(out_fname)
            # transfer everything in OUT_PATH to the ftp server
            self._transfer_files()
        elif msg.topic==mqtt_topics.MqttTopics.SKY_EYE_RESET_IMAGE_CAPTURE:
            print("quitting loop")
            quit_flag = True
        else:
            print(f"unhandled topic {msg.topic}")
        #
        return quit_flag        

    def _transfer_files(self):
        ftp = ftplib.FTP()

        # make a list of files in self.image_dir
        file_paths_l = [f for f in self.image_dir.glob("*")]
        
        if len(file_paths_l) == 0:
            return

        ftp.connect(self.ftp_server_addr, self.ftp_server_port)
        time.sleep(0.25)  # give connection time to settle; this pause considerably improves reliability
        ftp.login(self.ftp_user, self.ftp_passwd)
        ftp.set_pasv(True)
        
        for file_path in file_paths_l:
            print(f"transferring {file_path}")
            with open(file_path, "rb") as f:
                ftp.storbinary(f"STOR {file_path.name}", f)
            #
            # delete the file
            print(f"deleting {file_path}")
            file_path.unlink()
        #
        ftp.quit()

    def _run_once(self, inject_mqtt_msg=None, now_dt = None):

        #
        # if msg specified, then stick it in the queue (for debugging)
        if inject_mqtt_msg != None:
            self.mqtt.queue_msg(inject_mqtt_msg)
        #

        # reconnect, send i'm alive, etc.
        self._do_loop_tasks(now_dt = now_dt)
        
        # handle received messages
        quit_flag = False
        while  self.mqtt.queue_is_empty()==False:  # process all messages in the queue
            msg = self.mqtt.dequeue_msg()
            quit_flag = quit_flag or self._handle_msg(msg)  # _handle_msg can return True to exit loop
        #          

        return quit_flag


    def run(self):
        quit_flag = False
        while quit_flag==False:
            quit_flag = self._run_once()                                                    
            time.sleep(0.25)
        #

        #
        print("exiting sky-eye")                                                                                                      
    #   



def get_candidate_camera_indices():
    candidate_indices = []
    
    # Iterate over a range of numbers to check for camera indices
    for index in range(10):
        cap = cv2.VideoCapture(index)
        
        # Check if the camera is opened successfully
        if cap.isOpened():
            candidate_indices.append(index)
        
        # Release the camera
        cap.release()
    
    return candidate_indices

# write a function to parse arguments
# the first argument is "cmd"
# possible commands are "capturenow", "listcams", and "run"
# "capturenow" takes a camera index and a file path
# "listcams" takes no arguments
# "run" takes no arguments

cmds_l = {"capturenow", "listcams", "run"}
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help=f"command to run, {cmds_l}")
    parser.add_argument("-c", "--cam_index", help="capturenow: camera index", type=int)
    parser.add_argument("-o", "--out_fname", type=Path, help="capturenow: output filename")
    parser.add_argument("-j", "--config_fname", type=Path, help="run: config json file")
    args = parser.parse_args()

    return args

if __name__=="__main__":
    args = parse_args()
    if args.cmd=="capturenow":
        frame = SkyEye.grab_camera_frame(args.cam_index)
        if frame is not None:
            
            # Write the frame to the output file
            out_fname = "capturenow.jpg"
            cv2.imwrite(out_fname, frame)
            print(f"wrote {out_fname}")

            # display the image
            cv2.imshow('camera {self.camera_index}', frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        #
    elif args.cmd=="listcams":
        camera_indices_l = get_candidate_camera_indices()
        print(camera_indices_l)
    elif args.cmd=="run":
        eye = SkyEye(args.config_fname)
        eye.run()
    else:
        print(f"unknown command {args.cmd}")
        sys.exit(1)
