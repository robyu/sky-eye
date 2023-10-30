class MqttTopics:
    #
    # image capture
    STOVE_IMAGECAP_TOPIC   = "home/stove-image-capture"
    IC_CAPTURE_NOW         = f"{STOVE_IMAGECAP_TOPIC}/camera/capture-now"
    IC_RESET_IMAGE_CAPTURE = f"{STOVE_IMAGECAP_TOPIC}/reset/set"

    # stovewatcher
    STOVE_WATCHER_TOPIC = "home/stove-watcher"
    STOVE_STATUS_ON_DURATION_MIN = f"{STOVE_WATCHER_TOPIC}/stove-status/on-duration-min"
    STOVE_STATUS_ON_TO_OFF       = f"{STOVE_WATCHER_TOPIC}/stove-status/on-to-off"
    
    #alertbot
    ALERTBOT_IP_ADDR="home/alert-bot/ip_addr"
    