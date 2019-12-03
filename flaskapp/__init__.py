import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, current_app

from utils.config import get_config


def create_app():

    # create flask app
    config = get_config()
    app = Flask(__name__)
    app.config.from_object(config)

    # setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/webthing.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

    app.logger.info('Webthing Startup')

    # register handlers/routes
    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
