import pika
import ssl
import json

from utils.config import config


class Amqp:
    def __init__(self, host='localhost', port=5672, use_ssl=False,
                 user='guest', password='guest',
                 virtual_host='/', exchange='amq.topic'):
        """
        Creates a new connection
        """
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passw = password
        self.__vhost = virtual_host
        self.__exchange = exchange
        self.__amqp_channels = {}
        self.__msg_headers = {}

        credentials = pika.PlainCredentials(self.__user, self.__passw)

        if use_ssl:
            # enable SSL (server side cert)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            ssl_options = pika.SSLOptions(context=ctx, server_hostname=host)

            parameters = pika.ConnectionParameters(host=self.__host,
                                                   port=self.__port,
                                                   virtual_host=self.__vhost,
                                                   credentials=credentials,
                                                   ssl_options=ssl_options)

        else:
            # plain TCP
            parameters = pika.ConnectionParameters(host=self.__host,
                                                   port=self.__port,
                                                   virtual_host=self.__vhost,
                                                   credentials=credentials)

        self.__amqp_connection = pika.BlockingConnection(parameters)

        # create default channel
        self.__amqp_channels[1] = self.__amqp_connection.channel(1)
        self.__amqp_channels[1].exchange_declare(exchange=self.__exchange,
                                                 exchange_type='topic',
                                                 durable=True)

    def set_msg_headers(self, headers):
        """
        Set message headers that will be attached when publishing images, json, etc. messages
        """
        self.__msg_headers = headers

    def get_msg_headers(self, **kwargs):
        """
        returns set amqp message headers (also updated with provided parameters)
        """
        return {**self.__msg_headers, **kwargs}

    def channel(self, channel_number=None):
        """
        returns a channel to use.
        """
        if not channel_number:
            return self.__amqp_channels[1]

        else:
            channel = self.__amqp_channels.get(channel_number, None)
            if channel:
                return channel

            else:
                channel = self.__amqp_connection.channel(channel_number)
                self.__amqp_channels[channel_number] = channel
                return channel

    def subscribe(self, callback, routing_key, channel_number=None):
        """
        Create queue, bind it and start consuming
        """
        ch = self.channel(channel_number)
        result = ch.queue_declare('', exclusive=True, auto_delete=True)
        queue_name = result.method.queue

        ch.queue_bind(exchange=self.__exchange, queue=queue_name, routing_key=routing_key)
        ch.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    def process_data_events(self, timeout):
        """
        Consume all data events
        """
        try:
            self.__amqp_connection.process_data_events(time_limit=timeout)

        except Exception:
            pass

    def publish(self, routing_key, body, content_type, headers=None):
        """
        Publish new data.
        Always uses channel 1
        """
        self.channel().basic_publish(exchange=self.__exchange,
                                     routing_key=routing_key,
                                     body=body,
                                     properties=pika.BasicProperties(
                                        content_type=content_type,
                                        headers=headers
                                     ))

    def publish_message(self, msg_type, routing_key, message, timestamp,
                        encoder=json.dumps, content_type='application/json'):
        """
        Publish new data, with additional header fields (msg_type, routing_key, timestamp, etc.)
        Always uses channel 1
        """
        self.publish(routing_key=routing_key,
                     body=encoder(message),
                     content_type=content_type,
                     headers=self.get_msg_headers(
                                        msg_type=msg_type,
                                        routing_key=routing_key,
                                        timestamp=timestamp)
                     )


__the_amqp = None


def amqp():
    """
    Creates an AMQP client instance
    """
    global __the_amqp
    if not __the_amqp:
        cfg = config()
        cfg.get('AMQP_EXCHANGE', 'amq.topic')
        cfg.get('AMQP_HOST', 'localhost')
        cfg.get('AMQP_PORT', 5672)
        cfg.get('AMQP_VIRTUAL_HOST', '/')
        cfg.get('AMQP_USE_SSL', False)

        __the_amqp = Amqp(host=cfg.AMQP_HOST,
                          port=cfg.AMQP_PORT,
                          use_ssl=cfg.AMQP_USE_SSL,
                          user=cfg.AMQP_USERNAME,
                          password=cfg.AMQP_PASSWORD,
                          virtual_host=cfg.AMQP_VIRTUAL_HOST,
                          exchange=cfg.AMQP_EXCHANGE)

    return __the_amqp
