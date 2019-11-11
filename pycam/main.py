import base64
import time
import json

from config import config
from amqp import amqp
from cvcam import cv
from stats import stats, stats_config


def seconds2ns(secs):
    return int(secs * 10 ** 9)


class App:
    # camera constants
    CAM_ID = config()['cam_id']
    CAP_TOPIC_FRAME = "pycam.captures.%s.frame.jpeg" % (CAM_ID)
    CAP_TOPIC_STILL = "pycam.captures.%s.still.jpeg" % (CAM_ID)
    CMD_TOPIC = "pycam.control.%s" % (CAM_ID)
    IDLE_FRAME_TIMEOUT_S = 4.0
    ACTIVE_FRAME_TIMEOUT_S = 0.2
    ACTIVE_STATE_TIMEOUT_S = 5.0
    IDLE_FRAME_TIMEOUT_NS = seconds2ns(IDLE_FRAME_TIMEOUT_S)
    ACTIVE_FRAME_TIMEOUT_NS = seconds2ns(ACTIVE_FRAME_TIMEOUT_S)
    ACTIVE_STATE_TIMEOUT_NS = seconds2ns(ACTIVE_STATE_TIMEOUT_S)
    CMD_LOOP_TIMEOUT = ACTIVE_FRAME_TIMEOUT_S / 2

    # camera state
    cam = cv
    td_frame = IDLE_FRAME_TIMEOUT_NS
    ts_next_frame = 0
    ts_stop_active_state = 0

    @classmethod
    def wake_up(cls):
        cls.td_frame = cls.ACTIVE_FRAME_TIMEOUT_NS
        cls.ts_stop_active_state = time.time_ns() + cls.ACTIVE_STATE_TIMEOUT_NS

    @classmethod
    def sleep(cls):
        cls.td_frame = cls.IDLE_FRAME_TIMEOUT_NS

    @classmethod
    def do_state(cls):
        if time.time_ns() > cls.ts_stop_active_state:
            cls.sleep()


def command_callback(ch, method, properties, body):
    """
    Camera command callback
    Command format:
        {
            command: <string>,
            client: <string>,
            user: <string>
            [optional command specific values]
        }
    """
    try:
        cmd_obj = json.loads(body)
        print("cmd: %s" % (cmd_obj))

        if cmd_obj['command'] == 'wake_up':
            App.wake_up()

        elif cmd_obj['command'] == 'capture':
            readAndPublishStill()

    except Exception as e:
        print("cmd error: %s" % str(e))


def readAndPublishFrames():
    """
    Read a JPEG low-res frame from camera and publish on topic
    """
    if time.time_ns() > App.ts_next_frame:
        stats().incr('frames')
        with stats().timer('cv.read.frame'):
            encimg = App.cam().capture_jpeg_frame()
            imgblob = base64.b64encode(encimg)
            amqp().publish(routing_key=App.CAP_TOPIC_FRAME, body=imgblob)

        App.ts_next_frame = time.time_ns() + App.td_frame


def readAndPublishStill():
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    stats().incr('stills')
    encimg = cam().capture_jpeg_still()
    imgBlob = base64.b64encode(encimg)
    amqp().publish(routing_key=App.CAP_TOPIC_STILL, body=imgBlob)


def main():
    # create camera command subscription
    amqp().subscribe(channel_number=2, callback=command_callback, routing_key=App.CMD_TOPIC)

    # main loop
    while True:
        # read from AMQP (callback will be called on data events)
        with stats().timer('amqp.read.events'):
            amqp().process_data_events(App.CMD_LOOP_TIMEOUT)

        # read from camera
        readAndPublishFrames()

        # state checks
        App.do_state()

if __name__ == "__main__":
    main()
