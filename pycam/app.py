import time
import json
import logging
import base64
from enum import Enum

from utils.config import config
from utils.amqp import amqp
from utils.cvcam import cvcap
from utils.stats import stats
from utils.health import device
from utils.messages import *


"""
 Global/startup init
 - setup logging since other modules might need it
 - select correct camera, etc.
"""
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
cam = cvcap


def seconds2ns(secs):
    return int(secs * 10 ** 9)


def load_config():
    """
    Load device config from environment.
    """
    cfg = config()

    # user details
    cfg.AMQP_USERNAME = cfg.get('AMQP_USERNAME', 'guest')
    cfg.AMQP_PASSWORD = cfg.get('AMQP_PASSWORD', 'guest')

    # topic
    cfg.get('CAMERA_ID', 'CAM0')
    cfg.get('TOPIC_FRAME', "%s.%s.frame.jpeg" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))
    cfg.get('TOPIC_STILL', "%s.%s.still.jpeg" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))
    cfg.get('TOPIC_HEARTBEAT', "%s.%s.heartbeat" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))
    cfg.get('TOPIC_CMD', "%s.%s.control" % (cfg.AMQP_USERNAME, cfg.CAMERA_ID))

    # camera config
    cfg.IDLE_FRAME_TIMEOUT_S = 4.0
    cfg.ACTIVE_FRAME_TIMEOUT_S = 0.2
    cfg.HEALTH_CHECK_TIMEOUT_S = 5.0
    cfg.CMD_LOOP_TIMEOUT = cfg.ACTIVE_FRAME_TIMEOUT_S / 2

    cfg.IDLE_FRAME_TIMEOUT_NS = seconds2ns(cfg.IDLE_FRAME_TIMEOUT_S)
    cfg.ACTIVE_FRAME_TIMEOUT_NS = seconds2ns(cfg.ACTIVE_FRAME_TIMEOUT_S)
    cfg.HEALTH_CHECK_TIMEOUT_NS = seconds2ns(cfg.HEALTH_CHECK_TIMEOUT_S)

    return cfg


class State:
    """
    Application state and variables.
    """
    class STATE(Enum):
        """
        Possible app states (awake, sleep, etc)
        """
        NONE = 0
        SLEEP = 1
        WAKE = 2

    @classmethod
    def init(cls):
        cls.cfg = load_config()

        cls.td_frame = cls.cfg.IDLE_FRAME_TIMEOUT_NS
        cls.td_health = cls.cfg.IDLE_FRAME_TIMEOUT_NS
        cls.ts_next_frame = 0
        cls.ts_next_healthcheck = 0
        cls.ts_stop_active_state = 0
        cls.state = cls.STATE.NONE

    @classmethod
    def wake_up(cls, ts):
        """
        Reset idle/sleep timer and wake up if required.
        """
        if cls.state != cls.STATE.WAKE:
            logging.info('state - %s' % (cls.state.name))
            cls.td_frame = cls.cfg.ACTIVE_FRAME_TIMEOUT_NS
            cls.state = cls.STATE.WAKE
            cls.ts_next_frame = ts

        cls.ts_stop_active_state = ts + cls.cfg.IDLE_FRAME_TIMEOUT_NS

    @classmethod
    def try_sleep(cls, ts):
        """
        Test idle/sleep timer and go to sleep if required
        """
        if cls.state != cls.STATE.WAKE:
            if ts > cls.ts_stop_active_state:
                logging.info('state - %s' % (cls.STATE.WAKE))
                cls.td_frame = cls.cfg.IDLE_FRAME_TIMEOUT_NS
                cls.state = cls.STATE.WAKE


def try_read_and_pub_frame(ts):
    """
    Read a JPEG low-res frame from camera and publish on topic
    """
    if ts > State.ts_next_frame:
        encimg = cam().capture_jpeg_frame()
        amqp().publish_message(msg_type='frame',
                               routing_key=config().TOPIC_FRAME,
                               message=encimg,
                               timestamp=ts,
                               encoder=base64.b64encode,
                               content_type='image/jpeg')

        State.ts_next_frame = ts + State.td_frame


def try_read_and_pub_still(ts):
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    encimg = cam().capture_jpeg_still()
    amqp().publish_message(msg_type='still',
                           routing_key=config().TOPIC_FRAME,
                           message=encimg,
                           timestamp=ts,
                           encoder=base64.b64encode,
                           content_type='image/jpeg')



def try_check_and_pub_health(ts):
    """
    Check health and send out hearthbeat.
    """
    if ts > State.ts_next_healthcheck:
        amqp().publish_message(msg_type='hbeat',
                               routing_key=config().TOPIC_HEARTBEAT,
                               message=device().get_health(),
                               timestamp=ts,
                               encoder=encode_message,
                               content_type=encoded_content_type())

        State.ts_next_healthcheck = ts + State.td_health


def command_callback(ch, method, properties, body):
    """
    Camera command callback (see messages.py, for list of messages)
    """
    try:
        ts = time.time_ns()
        cmd_obj = decode_message(body, properties.content_type)

        if cmd_obj is not None:
            logging.info("object received: %s" % (cmd_obj))

            if type(cmd_obj) == Command:
                if cmd_obj.name == 'wake_up':
                    State.wake_up(ts)

                elif cmd_obj.name == 'capture':
                    try_read_and_pub_still(ts)

    except Exception as e:
        logging.exception("cmd error: %s" % str(e))


def main():
    # load config and init
    State.init()

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
        State.try_sleep(ts)


if __name__ == '__main__':
    main()
