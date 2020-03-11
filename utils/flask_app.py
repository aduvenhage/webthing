
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from utils.config import config, setup_logger_handlers


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

    cfg.SQLALCHEMY_DATABASE_URI = cfg.DATABASE_URL
    cfg.SQLALCHEMY_TRACK_MODIFICATIONS = False

    cfg.get('SECRET_KEY', None)
    if cfg.SECRET_KEY is None:
        raise Exception('No value specified for SECRET_KEY')

    # create flask app
    app = Flask(__name__,
                template_folder=os.path.join(cfg.base_dir, 'templates'),
                static_folder=os.path.join(cfg.base_dir, 'static'))

    app.config.from_object(cfg)

    # setup logging
    setup_logger_handlers(app.logger)

    if cfg.debug:
        app.logger.setLevel(logging.DEBUG)
        app.config['EXPLAIN_TEMPLATE_LOADING'] = True

    else:
        app.logger.setLevel(logging.INFO)

    app.logger.info(cfg.APP_NAME + ' Startup')

    # setup DB and auth
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    return app
