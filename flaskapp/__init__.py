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


def create_app():
    """
    Create flask application instance.
    """

    # get app config
    cfg = config()
    cfg.SQLALCHEMY_DATABASE_URI = config.DATABASE_URL
    cfg.SQLALCHEMY_TRACK_MODIFICATIONS = False

    cfg.get('SECRET_KEY', None)
    if cfg.SECRET_KEY is None:
        raise Exception('No value specified for SECRET_KEY')

    # create flask app
    app = Flask(__name__)
    app.config.from_object(config)

    # setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/webthing.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)

    app.logger.addHandler(file_handler)

    if cfg.DEBUG:
        app.logger.setLevel(logging.DEBUG)
    else:
        app.logger.setLevel(logging.INFO)

    app.logger.info('Webthing Startup')

    # setup DB and auth
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # register handlers/routes
    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
