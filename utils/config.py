import os
import dotenv
import logging
from logging.handlers import RotatingFileHandler


class Config():
    """
    Simple config class.

    Usage:
    - 'config()' function creates and returns one global config object.
    - 'config.get(...)' reads in values from environment.
    - 'config.property_name' returns config value if object has no attribute with that name.
    - i.e. can overwrite config values with 'config.property_name = ...'
    """

    def __init__(self):
        # load config defaults
        self.config = {}
        self.debug = self.get('DEBUG', False)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.get('DATABASE_URL', 'sqlite:///' + os.path.join(self.base_dir, 'webthing.db'))

        # TODO: load 'config.ini' (should override defaults)

        # load config from environment (overrides defaults and 'config.init' values)
        # NOTE: deployment should load .env file by default
        if self.debug:
            dotenv.load_dotenv('debug.env', override=True)

        self.get('APP_NAME', __name__)
        self.get('LOG_FILENAME', self.APP_NAME + '.log')

        # test config
        if not self.get('WEBTHING', False):
            raise AttributeError("Failed to load valid config. Try specifying 'DEBUG=True' in environment.")

        # configure logging defaults
        logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.DEBUG)

    def get(self, key, default):
        """
        Try to find value from environment or use default. Also casts value to the type of the supplied default.
        """
        if key in self.config:
            return self.config[key]

        else:
            if default is None:
                value = os.getenv(key)

            elif isinstance(default, bool):
                value = os.getenv(key, str(default))
                value = value in ['True', 'TRUE', 'true']

            else:
                value = type(default)(os.getenv(key, str(default)))

            self.config[key] = value
            return value

    def __getattr__(self, name):
        """
        Returns value from config dict if name is not an attribute of config object.
        """
        if name in self.config:
            return self.config[name]

        else:
            raise AttributeError('Unknown attribute %s' % (name))

    def __dir__(self):
        """
        Built list of all object attributes.
        """
        return list(self.__dict__.keys()) + list(self.config.keys())


__the_config = None


def config():
    """
    Returns global config object
    """
    global __the_config
    if not __the_config:
        __the_config = Config()

    return __the_config


def setup_logger_handlers(logger):
    cfg = config()
    if len(logger.handlers) == 0:
        # setup rotating file based logs
        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler(
            os.path.join('logs', cfg.LOG_FILENAME),
            maxBytes=1024*64,
            backupCount=64
        )

        file_handler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        )

        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)


def get_logger(name):
    cfg = config()

    logger = logging.getLogger(name)
    if cfg.debug:
        logger.setLevel(logging.DEBUG)

    else:
        logger.setLevel(logging.INFO)

    setup_logger_handlers(logger)

    return logger
