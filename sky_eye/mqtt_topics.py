class MqttTopics:
    #
    # image capture
    SKY_EYE_TOPIC   = "home/sky-eye"
    SKY_EYE_CAPTURE_NOW         = f"{SKY_EYE_TOPIC}/camera/capture-now"
    SKY_EYE_RESET_IMAGE_CAPTURE = f"{SKY_EYE_TOPIC}/reset/set"
    SKY_EYE_CONNECTED           = f"{SKY_EYE_TOPIC}/connected"
    SKY_EYE_IM_ALIVE            = f"{SKY_EYE_TOPIC}/imalive"

    # stovewatcher
    STOVE_WATCHER_TOPIC = "home/stove-watcher"
    STOVE_STATUS_ON_DURATION_MIN = f"{STOVE_WATCHER_TOPIC}/stove-status/on-duration-min"
    STOVE_STATUS_ON_TO_OFF       = f"{STOVE_WATCHER_TOPIC}/stove-status/on-to-off"
    
    #alertbot
    ALERTBOT_IP_ADDR="home/alert-bot/ip_addr"
    
