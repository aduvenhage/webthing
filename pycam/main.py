import base64
import time
import json

from config import config
from amqp import amqp
from cvcam import cv
from stats import stats, stats_config


# camera config
cam = cv
cap_topic_frame = config()['cap_topic_frame']
cap_topic_still = config()['cap_topic_still']
cmd_topic = config()['cmd_topic']


def command_callback(ch, method, properties, body):
    """
    Camera command callback
    """
    try:
        cmd_obj = json.loads(body)
        print("cmd: %s" % (cmd_obj))

    except Exception as e:
        print("cmd error: %s" % str(e))


def readAndPublishFrame():
    """
    Read a JPEG lowr-res frame from camera and publish on topic
    """
    encimg = cam().capture_jpeg_frame()
    imgBlob = base64.b64encode(encimg)
    amqp().publish(routing_key=cap_topic_frame, body=imgBlob)


def readAndPublishStill():
    """
    Read a JPEG high-res still from camera and publish on topic
    """
    encimg = cam().capture_jpeg_still()
    imgBlob = base64.b64encode(encimg)
    amqp().publish(routing_key=cap_topic_still, body=imgBlob)


def main():
    # create camera command subscription
    amqp().subscribe(channel_number=2, callback=command_callback, routing_key=cmd_topic)

    while True:
        # read from AMQP (callback will be called on data events)
        with stats().timer('amqp.read.events'):
            amqp().process_data_events()

        # read from camera
        with stats().timer('cv.read.frame'):
            readAndPublishFrame()

        # stuff
        stats().incr('frames')
        time.sleep(0.1)


if __name__ == "__main__":
    main()
