import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension
from settings_default import Development, Production, Testing


BASE_DIR = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """

    """
    app = Flask(__name__)
    app.config.from_envvar('YOURAPPLICATION_SETTINGS')
    if app.config['APP_MODE'] == 'dev':
        app.config.from_object(Development)
    elif app.config['APP_MODE'] == 'prod':
        app.config.from_object(Production)
    elif app.config['APP_MODE'] == 'test':
        app.config.from_object(Testing)
    app.config.from_object('settings_user')
    db.init_app(app)
    migrate.init_app(app, db)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if app.debug:
        DebugToolbarExtension(app)

    if not app.debug and not app.testing:

        # Logging
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/fhe.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Facebook Hidden Engagement')

    return app


from app import models
