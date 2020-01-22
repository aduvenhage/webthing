
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from utils.config import config


# globals
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_flask_app():
    """
    Create flask application instance.
    """

    # get app config 
    cfg = config()
    cfg.get('APP_NAME', 'Webthing')
    cfg.get('LOG_FILENAME', cfg.APP_NAME + '.log')

    cfg.SQLALCHEMY_DATABASE_URI = cfg.DATABASE_URL
    cfg.SQLALCHEMY_TRACK_MODIFICATIONS = False

    cfg.get('SECRET_KEY', None)
    if cfg.SECRET_KEY is None:
        raise Exception('No value specified for SECRET_KEY')

    # create flask app
    app = Flask(__name__)
    app.config.from_object(cfg)

    # setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler(os.path.join('logs', cfg.LOG_FILENAME), maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)

    if cfg.DEBUG:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    app.logger.info(cfg.APP_NAME + ' Startup')

    # setup DB and auth
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    return app
