import base64
import time

from config import config
from amqp import amqp
from cvcam import cv
from stats import stats, stats_config


def command_callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


def main():
    # create camera command subscription
    amqp().subscribe(channel_number=2, callback=command_callback, routing_key=config()['cmd_topic'])

    while True:
        # read from AMQP (callback will be called on data events)
        amqp().process_data_events()

        # read one frame
        with stats().timer('cv.imgread'):
            encimg = cv().capture_jpeg_frame()
            print('jpeg = %d bytes' % (int(encimg.nbytes)))

        # publish frame
        with stats().timer('cv.imgb64'):
            imgBlob = base64.b64encode(encimg)

        print('b64 = %d bytes' % (len(imgBlob)))

        with stats().timer('cv.imgpub'):
            amqp().publish(routing_key=config()['cap_topic'], body=imgBlob)

        # stuff
        stats().incr('frames')
        time.sleep(0.1)


if __name__ == "__main__":
    main()
