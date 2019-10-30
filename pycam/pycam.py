
import pika
import cv2
import statsd
import base64


amqp_connection = None
amqp_channels = {}
cv_cap = None
stats_client = None
helpMe = None


def amqp_connect():
    """
    Creates a new connection and returns it
    """
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters(host='localhost', 
                                           port=5672,
                                           virtual_host='/',
                                           credentials=credentials)

    return pika.BlockingConnection(parameters)


def amqp(channel_number=None, exchange='surveillance'):
    """
    Connects and returns a channel to use.
    """

    global amqp_connection

    if not amqp_connection:
        amqp_connection = amqp_connect()
        amqp_channels[1] = amqp_connection.channel(1)
        amqp_channels[1].exchange_declare(exchange=exchange, exchange_type='topic')

    if not channel_number:
        return amqp_channels[1]

    else:
        channel = amqp_channels.get(channel_number, None)
        if channel:
            return channel

        else:
            channel = amqp_connection.channel(channel_number)
            amqp_channels[channel_number] = channel
            return channel


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


def stats():
    global stats_client

    if not stats_client:
        stats_client = statsd.StatsClient('localhost', 8125)

    return stats_client


def cv():
    global cv_cap

    if not cv_cap:
        cv_cap = cv2.VideoCapture(0)

    return cv_cap


def main():

    # create subscription
    result = amqp().queue_declare('', exclusive=True, auto_delete=True)
    queue_name = result.method.queue
    amqp().queue_bind(exchange='surveillance', queue=queue_name, routing_key="pycam.captures.#")

    # start reads
    amqp().basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    while True:
        try:
            amqp_connection.process_data_events(time_limit=0)

        except pika.exceptions.ConnectionClosed:
            break

        # read one frame
        with stats().timer('cv.imgread'):
            ret, frame = cv().read()

        if ret:
            print('frame = %d bytes' % (int(frame.nbytes)))

            # display frame
            with stats().timer('cv.imshow'):
                cv2.imshow('frame', frame)

            # encode frame
            with stats().timer('cv.imgencode'):
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 10]
                result, encimg = cv2.imencode('.jpg', frame, encode_param)

            print('jpeg = %d bytes' % (int(encimg.nbytes)))

            # publish frame
            with stats().timer('cv.imgb64'):
                imgBlob = base64.b64encode(encimg)

            print('b64 = %d bytes' % (len(imgBlob)))

            with stats().timer('cv.imgpub'):
                amqp(2).basic_publish(exchange='surveillance', routing_key='pycam.captures.cam1.jpeg', body=imgBlob)

            # wait, message queue, draw and stuff ...
            with stats().timer('cv.wait'):
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            stats().incr('frames')


if __name__== "__main__":
  main()