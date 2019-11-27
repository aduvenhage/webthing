import os


class Config():
    """
    Simple config class.

    Usage:
    - 'get_config()' function creates and returns one global config object.
    - 'config.get(...)' reads in values from environment.
    - 'config.property_name' returns config value if object has no attribute with that name.
    - i.e. can overwrite config values with 'config.property_name = ...'
    """

    def __init__(self):
        """
        Setup some config attributes to start with.
        """
        self.config = {}
        self.get('CAMERA_ID', 'CAM0')
        self.get('CAMERA_URL', 0)
        self.get('JPEG_QUALITY', 90)
        self.get('VIDEO_WIDTH', 320)
        self.get('AMQP_EXCHANGE', 'amq.topic')
        self.get('AMQP_HOST', 'mysmarthome.co.za')
        self.get('AMQP_PORT', 5673)
        self.get('AMQP_VIRTUAL_HOST', '/')
        self.get('AMQP_USE_SSL', True)
        self.get('AMQP_USERNAME', 'guest')
        self.get('AMQP_PASSWORD', 'guest')
        self.get('STATS_HOST', 'localhost')
        self.get('STATS_PORT', 8125)

    def get(self, key, default):
        """
        Try to find value from environment or use default.
        """
        if key in self.config:
            return self.config[key]

        else:
            value = type(default)(os.getenv(key, str(default)))
            self.config[key] = value
            return value

    def __getattr__(self, name):
        """
        Returns value from config dict if name not an attribute of config object.
        """
        if name in self.config:
            return self.config[name]

        else:
            raise AttributeError('Unknown attribute %s' % (name))


__the_config = None


def get_config():
    """
    Returns global config object
    """
    global __the_config
    if not __the_config:
        __the_config = Config()

    return __the_config
