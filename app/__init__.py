"""
.. module::
    :platform: Linux
    :synopsis: Web-app to collect facebook metrics.

.. moduleauthor:: Stefan Kasberger <mail@stefankasberger.at>
"""


import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_debugtoolbar import DebugToolbarExtension


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """

    """
    app = Flask(__name__)
    YOURAPPLICATION_MODE = os.getenv('YOURAPPLICATION_MODE', default='DEVELOPMENT')
    print('* Updating App Mode to: ' + YOURAPPLICATION_MODE)
    travis = os.getenv('TRAVIS', default=False)
    if not travis:
        print('* Loading User Settings.')
        app.config.from_object('settings_user')
    if YOURAPPLICATION_MODE == 'DEVELOPMENT':
        print('* Loading Development Settings.')
        app.config['ENV'] = 'DEVELOPMENT'
        app.config.from_object('settings_default.Development')
        if not travis:
            DebugToolbarExtension(app)
    elif YOURAPPLICATION_MODE == 'PRODUCTION':
        print('* Loading Production Settings.')
        app.config['ENV'] = 'PRODUCTION'
        # order of settings loading: 1. settings file, 2. environment variable DATABASE_URL, 3. environment variable SQLALCHEMY_DATABASE_URI
        if not travis:
            app.config.from_pyfile(BASE_DIR+'/settings_production.py', silent=True)
        app.config.from_object('settings_default.Production')
    elif YOURAPPLICATION_MODE == 'TESTING':
        print('* Loading Test Settings.')
        app.config['ENV'] = 'TESTING'
        app.config.from_object('settings_default.Testing')
    print('* Database: ' + app.config['SQLALCHEMY_DATABASE_URI'])
    db.init_app(app)
    migrate.init_app(app, db)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:

        # Logging (only production)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/fhe.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Facebook Hidden Engagement')

    return app


from app import models
