import base64
import time
import json
import logging

from config import config
from amqp import amqp
from cvcam import cv
from stats import stats, stats_config


# setup
logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)


def seconds2ns(secs):
    return int(secs * 10 ** 9)


class App:
    """
    Camera App State
    """

    # camera constants
    CAM_ID = config()['cam_id']

    TOPIC_FRAME = "pycam.captures.%s.frame.jpeg" % (CAM_ID)
    TOPIC_STILL = "pycam.captures.%s.still.jpeg" % (CAM_ID)
    TOPIC_HEARTBEAT = "pycam.status.%s.heartbeat" % (CAM_ID)
    TOPIC_CMD = "pycam.control.%s" % (CAM_ID)

    IDLE_FRAME_TIMEOUT_S = 4.0
    ACTIVE_FRAME_TIMEOUT_S = 0.2
    HEALTH_CHECK_TIMEOUT_S = 5.0
    CMD_LOOP_TIMEOUT = ACTIVE_FRAME_TIMEOUT_S / 2

    IDLE_FRAME_TIMEOUT_NS = seconds2ns(IDLE_FRAME_TIMEOUT_S)
    ACTIVE_FRAME_TIMEOUT_NS = seconds2ns(ACTIVE_FRAME_TIMEOUT_S)
    HEALTH_CHECK_TIMEOUT_NS = seconds2ns(HEALTH_CHECK_TIMEOUT_S)

    # camera state
    cam = cv
    td_frame = IDLE_FRAME_TIMEOUT_NS
    td_healt = IDLE_FRAME_TIMEOUT_NS
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
            cls.td_frame = cls.ACTIVE_FRAME_TIMEOUT_NS
            cls.state = 'wake'
            cls.ts_next_frame = time.time_ns()

        cls.ts_stop_active_state = time.time_ns() + cls.IDLE_FRAME_TIMEOUT_NS

    @classmethod
    def try_sleep(cls, ts):
        """
        Test idle/sleep timer and go to sleep if required
        """
        if cls.state != 'sleep':
            if time.time_ns() > cls.ts_stop_active_state:
                logging.info('state - asleep')
                cls.td_frame = cls.IDLE_FRAME_TIMEOUT_NS
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
    if time.time_ns() > App.ts_next_frame:
        stats().incr('cam.frame_count')
        with stats().timer('cam.frame_time'):
            encimg = App.cam().capture_jpeg_frame()
            imgblob = base64.b64encode(encimg)
            amqp().publish(routing_key=App.TOPIC_FRAME, body=imgblob)

        App.ts_next_frame = time.time_ns() + App.td_frame


def read_and_pub_still(ts):
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    stats().incr('cam.still_count')
    with stats().timer('cam.still_time'):
        encimg = App.cam().capture_jpeg_still()
        imgBlob = base64.b64encode(encimg)
        amqp().publish(routing_key=App.TOPIC_STILL, body=imgBlob)


def try_check_and_pub_health(ts):
    """
    Check health and send out hearthbeat.
    """
    if time.time_ns() > App.ts_next_healthcheck:
        stats().incr('cam.heartbeat_count')
        with stats().timer('cam.heartbeat_time'):

            status = {
                'name': App.CAM_ID,
                'frame_timeout': App.td_frame
            }

            amqp().publish(routing_key=App.TOPIC_HEARTBEAT, body=json.dumps(status))

        App.ts_next_healthcheck = time.time_ns() + App.td_healt


def main():
    # create camera command subscription
    amqp().subscribe(channel_number=2, callback=command_callback, routing_key=App.TOPIC_CMD)

    # main loop
    while True:
        # read from AMQP (callback will be called on data events)
        with stats().timer('cam.data_proc_time'):
            amqp().process_data_events(App.CMD_LOOP_TIMEOUT)

        ts = time.time_ns()

        # read from camera
        try_read_and_pub_frame(ts)

        # check health and send out hearthbeat
        try_check_and_pub_health(ts)

        # state checks
        App.try_sleep(ts)


if __name__ == "__main__":
    main()
