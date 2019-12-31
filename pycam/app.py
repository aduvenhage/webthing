import time
import json
import logging
from utils.config import config
from utils.amqp import amqp
from utils.cvcam import cvcap
from utils.stats import stats
from utils.health import device


"""
 Global/startup init
 - setup logging since other modules might need it
 - select correct camera, etc.
"""
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
cam = cvcap


class Config:
    """
    Static config from environment.

    NOTE: Config (call Config.init()) has to be loaded before Application state is initialised (see State class).
    """

    @classmethod
    def init(cls):
        cls.config = config()

        # user details
        cls.config.AMQP_USERNAME = cls.config.get('AMQP_USERNAME', 'guest')
        cls.config.AMQP_PASSWORD = cls.config.get('AMQP_PASSWORD', 'guest')

        # topic
        cls.config.get('CAMERA_ID', 'CAM0')
        cls.config.get('TOPIC_FRAME', "%s.%s.frame.jpeg" % (cls.config.AMQP_USERNAME, cls.config.CAMERA_ID))
        cls.config.get('TOPIC_STILL', "%s.%s.still.jpeg" % (cls.config.AMQP_USERNAME, cls.config.CAMERA_ID))
        cls.config.get('TOPIC_HEARTBEAT', "%s.%s.heartbeat" % (cls.config.AMQP_USERNAME, cls.config.CAMERA_ID))
        cls.config.get('TOPIC_CMD', "%s.%s.control" % (cls.config.AMQP_USERNAME, cls.config.CAMERA_ID))

        # camera config
        cls.config.IDLE_FRAME_TIMEOUT_S = 4.0
        cls.config.ACTIVE_FRAME_TIMEOUT_S = 0.2
        cls.config.HEALTH_CHECK_TIMEOUT_S = 5.0
        cls.config.CMD_LOOP_TIMEOUT = cls.config.ACTIVE_FRAME_TIMEOUT_S / 2

        cls.config.IDLE_FRAME_TIMEOUT_NS = cls.seconds2ns(cls.config.IDLE_FRAME_TIMEOUT_S)
        cls.config.ACTIVE_FRAME_TIMEOUT_NS = cls.seconds2ns(cls.config.ACTIVE_FRAME_TIMEOUT_S)
        cls.config.HEALTH_CHECK_TIMEOUT_NS = cls.seconds2ns(cls.config.HEALTH_CHECK_TIMEOUT_S)

    @classmethod
    def seconds2ns(cls, secs):
        return int(secs * 10 ** 9)


class State:
    """
    Application state and variables.

    NOTE: Config (call Config.init()) has to be loaded before State is initialised.
    """

    @classmethod
    def init(cls):
        cls.config = config()

        cls.td_frame = cls.config.IDLE_FRAME_TIMEOUT_NS
        cls.td_health = cls.config.IDLE_FRAME_TIMEOUT_NS
        cls.ts_next_frame = 0
        cls.ts_next_healthcheck = 0
        cls.ts_stop_active_state = 0
        cls.state = ''

    @classmethod
    def wake_up(cls, ts):
        """
        Reset idle/sleep timer and wake up if required.
        """
        if cls.state != 'wake':
            logging.info('state - awake')
            cls.td_frame = cls.config.ACTIVE_FRAME_TIMEOUT_NS
            cls.state = 'wake'
            cls.ts_next_frame = ts

        cls.ts_stop_active_state = ts + cls.config.IDLE_FRAME_TIMEOUT_NS

    @classmethod
    def try_sleep(cls, ts):
        """
        Test idle/sleep timer and go to sleep if required
        """
        if cls.state != 'sleep':
            if ts > cls.ts_stop_active_state:
                logging.info('state - asleep')
                cls.td_frame = cls.config.IDLE_FRAME_TIMEOUT_NS
                cls.state = 'sleep'


def try_read_and_pub_frame(ts):
    """
    Read a JPEG low-res frame from camera and publish on topic
    """
    if ts > State.ts_next_frame:
        encimg = cam().capture_jpeg_frame()
        amqp().publish_jpeg_image(msg_type='frame',
                                  routing_key=config().TOPIC_FRAME,
                                  jpegimg=encimg,
                                  timestamp=ts)

        State.ts_next_frame = ts + State.td_frame


def try_read_and_pub_still(ts):
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    encimg = cam().capture_jpeg_still()
    amqp().publish_jpeg_image(msg_type='still',
                              routing_key=config().TOPIC_FRAME,
                              jpegimg=encimg,
                              timestamp=ts)


def try_check_and_pub_health(ts):
    """
    Check health and send out hearthbeat.
    """
    if ts > State.ts_next_healthcheck:
        amqp().publish_json_message(msg_type='hbeat',
                                    routing_key=config().TOPIC_HEARTBEAT,
                                    message=device().get_health(),
                                    timestamp=ts)

        State.ts_next_healthcheck = ts + State.td_health


def command_callback(ch, method, properties, body):
    """
    Camera command callback

        Command format:
        {
            command: str,
            value: ??
        }

    """
    try:
        ts = time.time_ns()
        cmd_obj = json.loads(body)
        logging.info("cmd received: %s" % (cmd_obj))

        if cmd_obj['command'] == 'wake_up':
            State.wake_up(ts)

        elif cmd_obj['command'] == 'capture':
            try_read_and_pub_still(ts)

    except Exception as e:
        logging.exception("cmd error: %s" % str(e))


def main():
    # load config and init
    Config.init()
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
