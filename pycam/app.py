import time
import logging
from enum import Enum

from utils.config import config
from utils.amqp import amqp
from utils.cvcam import cvcap
from utils.health import device
from utils.messages import encode_message, encoded_content_type
from utils.messages import decode_message
from utils.messages import Command


class STATE(Enum):
    """
    Possible app states (awake, sleep, etc)
    """
    NONE = 0
    SLEEP = 1
    WAKE = 2


class App:
    """
    Application state and variables.
    """
    cfg = None
    td_frame = 0
    td_health = 0
    ts_next_frame = 0
    ts_next_healthcheck = 0
    ts_stop_active_state = 0
    state = STATE.NONE
    cam = cvcap


def seconds2ns(secs):
    return int(secs * 10 ** 9)


def load_config():
    """
    Load device config from environment.
    """
    cfg = config()
    logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)

    # user details
    cfg.AMQP_USERNAME = cfg.get('AMQP_USERNAME', 'guest')
    cfg.AMQP_PASSWORD = cfg.get('AMQP_PASSWORD', 'guest')

    # camera config
    cfg.get('CAMERA_ID', 'CAM0')
    cfg.get('CAMERA_LOCATION', '')

    cfg.IDLE_FRAME_TIMEOUT_S = 4.0
    cfg.ACTIVE_FRAME_TIMEOUT_S = 0.2
    cfg.HEALTH_CHECK_TIMEOUT_S = 5.0
    cfg.CMD_LOOP_TIMEOUT = cfg.ACTIVE_FRAME_TIMEOUT_S / 2

    cfg.IDLE_FRAME_TIMEOUT_NS = seconds2ns(cfg.IDLE_FRAME_TIMEOUT_S)
    cfg.ACTIVE_FRAME_TIMEOUT_NS = seconds2ns(cfg.ACTIVE_FRAME_TIMEOUT_S)
    cfg.HEALTH_CHECK_TIMEOUT_NS = seconds2ns(cfg.HEALTH_CHECK_TIMEOUT_S)

    # GUID
    cfg.CAMERA_TOKEN = cfg.AMQP_USERNAME + '_' + cfg.CAMERA_ID

    # topics
    cfg.get('TOPIC_FRAME', "%s.%s.frame.jpeg" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))
    cfg.get('TOPIC_STILL', "%s.%s.still.jpeg" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))
    cfg.get('TOPIC_HEARTBEAT', "%s.%s.heartbeat" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))
    cfg.get('TOPIC_CMD', "%s.%s.control" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))

    # App State
    App.td_frame = cfg.IDLE_FRAME_TIMEOUT_NS
    App.td_health = cfg.IDLE_FRAME_TIMEOUT_NS
    App.cfg = cfg

    return cfg


def wake_up(ts):
    """
    Reset idle/sleep timer and wake up if required.
    """
    if App.state != STATE.WAKE:
        logging.info('state - %s' % (STATE.WAKE))
        App.td_frame = App.cfg.ACTIVE_FRAME_TIMEOUT_NS
        App.state = STATE.WAKE
        App.ts_next_frame = ts

    App.ts_stop_active_state = ts + App.cfg.IDLE_FRAME_TIMEOUT_NS


def try_sleep(ts):
    """
    Test idle/sleep timer and go to sleep if required
    """
    if App.state != STATE.SLEEP:
        if ts > App.ts_stop_active_state:
            logging.info('state - %s' % (STATE.SLEEP))
            App.td_frame = App.cfg.IDLE_FRAME_TIMEOUT_NS
            App.state = STATE.SLEEP


def try_read_and_pub_frame(ts):
    """
    Read a JPEG low-res frame from camera and publish on topic
    """
    if ts > App.ts_next_frame:
        App.ts_next_frame = ts + App.td_frame

        image = App.cam().capture_jpeg_frame()
        image.source = config().CAMERA_TOKEN

        amqp().publish(routing_key=config().TOPIC_FRAME,
                       body=encode_message(image),
                       content_type='application/json')


def try_read_and_pub_still(ts):
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    image = App.cam().capture_jpeg_still()
    image.source = config().CAMERA_TOKEN

    amqp().publish(routing_key=config().TOPIC_STILL,
                   body=encode_message(image),
                   content_type='application/json')


def try_check_and_pub_health(ts):
    """
    Check health and send out hearthbeat.
    """
    if ts > App.ts_next_healthcheck:
        App.ts_next_healthcheck = ts + App.td_health

        health = device().get_health()
        health.source = config().CAMERA_TOKEN

        amqp().publish(routing_key=config().TOPIC_HEARTBEAT,
                       body=encode_message(health),
                       content_type=encoded_content_type())


def command_callback(ch, method, properties, body):
    """
    Camera command callback (see messages.py, for list of messages)
    """
    try:
        ts = time.time_ns()
        obj = decode_message(body)

        if obj is not None:
            if type(obj) == Command:
                if obj.name == 'wake_up':
                    logging.info("'wake_up' command received")
                    wake_up(ts)

                elif obj.name == 'capture':
                    logging.info("'capture' command received")
                    try_read_and_pub_still(ts)

            else:
                logging.debug("message received: %s" % (obj))

    except Exception as e:
        logging.exception("cmd error: %s" % str(e))


def main():
    # load config and init
    load_config()

    # create camera command subscription
    amqp().subscribe(channel_number=2, callback=command_callback, routing_key=config().TOPIC_CMD)

    # main loop
    while True:
        # read from AMQP (callback will be called on data events)
        amqp().process_data_events(config().CMD_LOOP_TIMEOUT)
        ts = time.time_ns()

        # read from camera
        try_read_and_pub_frame(ts)

        # check health and send out hearthbeat
        try_check_and_pub_health(ts)

        # state checks
        try_sleep(ts)


if __name__ == '__main__':
    main()
