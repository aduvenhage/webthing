__config = {
    'cam_id': 'cam1',
}

__cv_config = {
    'device': 0,
    'jpeg_quality': 90,
    'video_width': 320
}

__amqp_config = {
    'exchange': 'amq.topic',
    'username': 'guest',
    'password': 'guest',
    'host': 'localhost',
    'port': 5672,
    'virtual_host': '/'
}

__stats_config = {
    'host': 'localhost',
    'port': 8125
}


def config():
    return __config


def cv_config():
    return __cv_config


def amqp_config():
    return __amqp_config


def stats_config():
    return __stats_config

