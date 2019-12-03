import base64
import time
import json
import logging

from utils.config import get_config
from utils.amqp import amqp
from utils.cvcam import cv
from utils.stats import stats



# setup
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)


def seconds2ns(secs):
    return int(secs * 10 ** 9)


class App:
    """
    Camera App State
    """

    # camera constants
    config = get_config()
    config.get('TOPIC_FRAME', "pycam.captures.%s.frame.jpeg" % (config.CAMERA_ID))
    config.get('TOPIC_STILL', "pycam.captures.%s.still.jpeg" % (config.CAMERA_ID))
    config.get('TOPIC_HEARTBEAT', "pycam.status.%s.heartbeat" % (config.CAMERA_ID))
    config.get('TOPIC_CMD', "pycam.control.%s" % (config.CAMERA_ID))

    config.IDLE_FRAME_TIMEOUT_S = 4.0
    config.ACTIVE_FRAME_TIMEOUT_S = 0.2
    config.HEALTH_CHECK_TIMEOUT_S = 5.0
    config.CMD_LOOP_TIMEOUT = config.ACTIVE_FRAME_TIMEOUT_S / 2

    config.IDLE_FRAME_TIMEOUT_NS = seconds2ns(config.IDLE_FRAME_TIMEOUT_S)
    config.ACTIVE_FRAME_TIMEOUT_NS = seconds2ns(config.ACTIVE_FRAME_TIMEOUT_S)
    config.HEALTH_CHECK_TIMEOUT_NS = seconds2ns(config.HEALTH_CHECK_TIMEOUT_S)

    # camera state
    cam = cv
    cam(config)

    td_frame = config.IDLE_FRAME_TIMEOUT_NS
    td_health = config.IDLE_FRAME_TIMEOUT_NS
    ts_next_frame = 0
    ts_next_healthcheck = 0
    ts_stop_active_state = 0
    state = ''

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


def command_callback(ch, method, properties, body):
    """
    Camera command callback
    Command format:
        {
            ???
        }
    """
    try:
        stats().incr('cam.cmd_count')
        with stats().timer('cam.cmd_times'):
            ts = time.time_ns()
            cmd_obj = json.loads(body)
            logging.info("cmd received: %s" % (cmd_obj))

            if cmd_obj['command'] == 'wake_up':
                App.wake_up(ts)

            elif cmd_obj['command'] == 'capture':
                read_and_pub_still(ts)

    except Exception as e:
        logging.exception("cmd error: %s" % str(e))


def try_read_and_pub_frame(ts):
    """
    Read a JPEG low-res frame from camera and publish on topic
    """
    if ts > App.ts_next_frame:
        stats().incr('cam.frame_count')
        with stats().timer('cam.frame_time'):

            # NOTE: using base 64 encoding to be compatible with JS front-end
            encimg = App.cam().capture_jpeg_frame()
            imgblob = base64.b64encode(encimg)
            amqp().publish(routing_key=App.config.TOPIC_FRAME, body=imgblob, content_type='image/jpeg')

        App.ts_next_frame = ts + App.td_frame


def read_and_pub_still(ts):
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    stats().incr('cam.still_count')
    with stats().timer('cam.still_time'):

        # NOTE: using base 64 encoding to be compatible with JS front-end
        encimg = App.cam().capture_jpeg_still()
        imgBlob = base64.b64encode(encimg)
        amqp().publish(routing_key=App.config.TOPIC_STILL, body=imgBlob, content_type='image/jpeg')


def try_check_and_pub_health(ts):
    """
    Check health and send out hearthbeat.
    """
    if ts > App.ts_next_healthcheck:
        stats().incr('cam.heartbeat_count')
        with stats().timer('cam.heartbeat_time'):

            status = {
                'name': App.config.CAMERA_ID,
                'frame_timeout': App.td_frame,
                'topic_still': App.config.TOPIC_STILL,
                'topic_frame': App.config.TOPIC_FRAME
            }

            amqp().publish(routing_key=App.config.TOPIC_HEARTBEAT, body=json.dumps(status), content_type='application/json')

        App.ts_next_healthcheck = ts + App.td_health


def main():
    # create camera command subscription
    amqp(App.config).subscribe(channel_number=2, callback=command_callback, routing_key=App.config.TOPIC_CMD)

    # main loop
    while True:
        # read from AMQP (callback will be called on data events)
        with stats(App.config).timer('cam.data_proc_time'):
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