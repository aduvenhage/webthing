from utils import flask_app


def create_app():
    app = flask_app.create_flask_app()

    # register handlers/routes
    from webapp.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from webapp.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from webapp.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
