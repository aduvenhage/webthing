import base64
import time
import json
import logging

from utils.config import get_config
from utils.amqp import amqp
from utils.cvcam import cvcap
from utils.stats import stats



# setup
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)


def seconds2ns(secs):
    return int(secs * 10 ** 9)


class App:

    @classmethod
    def init(cls):
        cls.config = get_config()

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

        cls.config.IDLE_FRAME_TIMEOUT_NS = seconds2ns(cls.config.IDLE_FRAME_TIMEOUT_S)
        cls.config.ACTIVE_FRAME_TIMEOUT_NS = seconds2ns(cls.config.ACTIVE_FRAME_TIMEOUT_S)
        cls.config.HEALTH_CHECK_TIMEOUT_NS = seconds2ns(cls.config.HEALTH_CHECK_TIMEOUT_S)

        # camera state
        cls.cam = cvcap

        cls.td_frame = cls.config.IDLE_FRAME_TIMEOUT_NS
        cls.td_health = cls.config.IDLE_FRAME_TIMEOUT_NS
        cls.ts_next_frame = 0
        cls.ts_next_healthcheck = 0
        cls.ts_stop_active_state = 0
        cls.state = ''

        # ampqp setuo
        cls.amqp_headers = {
            'source': cls.config.CAMERA_ID,
            'user': cls.config.AMQP_USERNAME
        }

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

    @classmethod
    def get_amqp_headers(cls, **kwargs):
        return {**cls.amqp_headers, **kwargs}


def command_callback(ch, method, properties, body):
    """
    Camera command callback
    Command format:
        {
            ???
        }
    """
    try:
        ts = time.time_ns()
        cmd_obj = json.loads(body)
        logging.info("cmd received: %s" % (cmd_obj))

        if cmd_obj['command'] == 'wake_up':
            App.wake_up(ts)

        elif cmd_obj['command'] == 'capture':
            read_and_pub_still(ts)

    except Exception as e:
        logging.exception("cmd error: %s" % str(e))


def pub_jpeg_image(msg_type, routing_key, jpegimg):
    imgblob = base64.b64encode(jpegimg)
    amqp().publish(routing_key=routing_key,
                   body=imgblob,
                   content_type='image/jpeg',
                   headers=App.get_amqp_headers(
                                    msg_type=msg_type,
                                    routing_key=routing_key)
                   )


def pub_json_message(msg_type, routing_key, message):
    amqp().publish(routing_key=routing_key,
                   body=json.dumps(message),
                   content_type='application/json',
                   headers=App.get_amqp_headers(
                                    msg_type=msg_type,
                                    routing_key=routing_key)
                   )


def try_read_and_pub_frame(ts):
    """
    Read a JPEG low-res frame from camera and publish on topic
    """
    if ts > App.ts_next_frame:
        # NOTE: using base 64 encoding to be compatible with JS front-end
        encimg = App.cam().capture_jpeg_frame()
        pub_jpeg_image(msg_type='frame',
                       routing_key=App.config.TOPIC_FRAME,
                       jpegimg=encimg)

        App.ts_next_frame = ts + App.td_frame


def read_and_pub_still(ts):
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    # NOTE: using base 64 encoding to be compatible with JS front-end
    encimg = App.cam().capture_jpeg_still()
    pub_jpeg_image(msg_type='still',
                   routing_key=App.config.TOPIC_FRAME,
                   jpegimg=encimg)


def try_check_and_pub_health(ts):
    """
    Check health and send out hearthbeat.
    """
    if ts > App.ts_next_healthcheck:
        status = {
            'name': App.config.CAMERA_ID,
            'frame_timeout': App.td_frame,
            'topic_still': App.config.TOPIC_STILL,
            'topic_frame': App.config.TOPIC_FRAME
        }

        pub_json_message(msg_type='hbeat',
                         routing_key=App.config.TOPIC_HEARTBEAT,
                         message=status)

        App.ts_next_healthcheck = ts + App.td_health


def main():
    # load config and init
    App.init()

    # create camera command subscription
    amqp().subscribe(channel_number=2, callback=command_callback, routing_key=App.config.TOPIC_CMD)

    # main loop
    while True:
        # read from AMQP (callback will be called on data events)
        amqp().process_data_events(App.config.CMD_LOOP_TIMEOUT)
        ts = time.time_ns()

        # read from camera
        try_read_and_pub_frame(ts)

        # check health and send out hearthbeat
        try_check_and_pub_health(ts)

        # state checks
        App.try_sleep(ts)


if __name__ == '__main__':
    main()
