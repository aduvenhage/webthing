import base64

from config import config
from amqp import amqp_channel, amqp_connection
from cvcam import cv_capture_jpeg_frame
from stats import stats, stats_config


def command_callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


def main():
    # create camera command subscription
    result = amqp_channel().queue_declare('', exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    amqp_channel().queue_bind(exchange='amq.topic', queue=queue_name, routing_key=config()['cmd_topic'])
    amqp_channel().basic_consume(queue=queue_name, on_message_callback=command_callback, auto_ack=True)

    while True:
        try:
            amqp_connection().process_data_events(time_limit=0)

        except Exception:
            break

        # read one frame
        with stats().timer('cv.imgread'):
            encimg = cv_capture_jpeg_frame()
            print('jpeg = %d bytes' % (int(encimg.nbytes)))

        # publish frame
        with stats().timer('cv.imgb64'):
            imgBlob = base64.b64encode(encimg)

        print('b64 = %d bytes' % (len(imgBlob)))

        with stats().timer('cv.imgpub'):
            amqp_channel(2).basic_publish(exchange='amq.topic', routing_key=config()['cap_topic'], body=imgBlob)

        # stuff
        stats().incr('frames')


if __name__ == "__main__":
    main()
