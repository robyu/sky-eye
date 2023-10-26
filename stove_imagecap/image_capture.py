import cv2
import argparse
import sys
from pathlib import Path
from stove_imagecap import config_store
import ftplib

OUT_PATH = Path("./out")
def capture_image(camera_index, file_path):
    cap = cv2.VideoCapture(camera_index)
    
    # Check if the camera is opened successfully
    if not cap.isOpened():
        print("Unable to open the camera")
        return
    
    # Read the frame from the camera
    ret, frame = cap.read()
    
    # Check if the frame was successfully read
    if not ret:
        print("Failed to capture frame from the camera")
        return
    
    # Save the captured image to a file
    cv2.imwrite(file_path, frame)
    print(f"wrote file to {file_path}")
    
    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

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
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd", help="command to run")
    parser.add_argument("-c", "--cam_index", help="camera index", type=int)
    parser.add_argument("-o", "--out_fname", type=Path, help="output filename")
    parser.add_argument("-j", "--config_fname", type=Path, help="config json file")
    args = parser.parse_args()
    return args

def transfer_file_to_ftp_server(file_path, ftp_server_addr, ftp_server_port):
    ftp = ftplib.FTP()
    ftp.connect(ftp_server_addr, ftp_server_port)
    ftp.login()
    with open(file_path, "rb") as f:
        ftp.storbinary(f"STOR {file_path.name}", f)
    ftp.quit()


def run(config_json, test_mqtt_client = None):
    config = ConfigStore(config_json)    
    print("hello world")   

    #    def __init__(self, broker_addr, test_client=None):
    mqtt_if = MqttIf(config.mqtt_broker_addr, test_client=test_mqtt_client)
    is_connected = mqtt_if.reconnect()
    assert is_connected, "mqtt_if.reconnect() failed"

    # create OUT_PATH if it does not exist
    if not OUT_PATH.exists():
        OUT_PATH.mkdir()
    # delete all files in OUT_PATH
    for file in OUT_PATH.iterdir():
        file.unlink()


    # set up a loop
    # within the loop, check for a message on the mqtt topic
    # if the message is "capture now", then capture an image
    while(True):
        mqtt_if.loop()  # look for messages
        if mqtt_if.msg_queue.empty()==True:
            continue
        else:
            msg = mqtt_if.msg_queue.get()
            print(f"received message {msg.payload} on topic {msg.topic}")
            if msg.topic==mqtt_topics.MqttTopics.IC_CAPTURE:
                # if msg argument is "", then generate a filename based on the time-date
                if msg.payload=="":
                    out_fname = OUT_PATH / f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
                else:
                    out_fname = Path(msg.payload)
                #
                capture_image(config.camera_index, out_fname)
                # transfer everything in OUT_PATH to the ftp server
                transfer_file_to_ftp_server(OUT_PATH, config.ftp_server_addr, config.ftp_server_port)
            elif msg.topic==mqtt_topics.MqttTopics.IC_RESET_IMAGE_CAPTURE:
                print("resetting")
            #
        #
        # sleep for a bit
        time.sleep(0.1)
    #


if __name__=="__main__":
    args = parse_args()
    if args.cmd=="capturenow":
        capture_image(args.cam_index, args.out_fname)
    elif args.cmd=="listcams":
        camera_indices_l = get_candidate_camera_indices()
        print(camera_indices_l)
    elif args.cmd=="run":
        assert args.config_fname.exists(), f"config file {args.config_fname} does not exist"
        print(args.json_file)
        run(args.config_fname)
    else:
        print(f"unknown command {args.cmd}")
        sys.exit(1)
