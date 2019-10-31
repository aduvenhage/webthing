import pika
from config import amqp_config


__amqp_connection = None
__amqp_channels = {}


def amqp_connection():
    """
    Creates a new connection and returns it
    """
    global __amqp_connection

    if not __amqp_connection:
        credentials = pika.PlainCredentials(amqp_config()['username'],
                                            amqp_config()['password'])

        parameters = pika.ConnectionParameters(host=amqp_config()['host'],
                                               port=5672,
                                               virtual_host=amqp_config()['virtual_host'],
                                               credentials=credentials)

        __amqp_connection = pika.BlockingConnection(parameters)

    return __amqp_connection


def amqp_channel(channel_number=None):
    """
    Connects and returns a channel to use.
    """
    global __amqp_channels

    if not __amqp_channels:
        __amqp_channels[1] = amqp_connection().channel(1)
        __amqp_channels[1].exchange_declare(exchange=amqp_config()['exchange'],
                                            exchange_type='topic',
                                            durable=True)

    if not channel_number:
        return __amqp_channels[1]

    else:
        channel = __amqp_channels.get(channel_number, None)
        if channel:
            return channel

        else:
            channel = amqp_connection().channel(channel_number)
            __amqp_channels[channel_number] = channel
            return channel


def amqp_subscribe(channel_number=None, callback=None, routing_key=None):
    """
    Create queue, bind it and start consuming
    """
    result = amqp_channel(channel_number).queue_declare('', exclusive=True, auto_delete=True)
    queue_name = result.method.queue

    amqp_channel().queue_bind(exchange=amqp_config()['exchange'], queue=queue_name, routing_key=routing_key)
    amqp_channel().basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)


def amqp_process_data_events():
    """
    Consume all data events
    """
    try:
        amqp_connection().process_data_events(time_limit=0)

    except Exception:
        pass
