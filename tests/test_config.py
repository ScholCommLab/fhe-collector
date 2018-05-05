import os
from app import create_app


BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


class TestConfiguration:
    def test_development_settings(self):
        """ Tests if the development config loads correctly """

        os.environ['YOURAPPLICATION_MODE'] = 'DEVELOPMENT'
        app = create_app()

        assert app.config['DEBUG'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

    def test_testing_settings(self):
        """ Tests if the test config loads correctly """

        os.environ['YOURAPPLICATION_MODE'] = 'TESTING'
        app = create_app()

        assert app.config['SQLALCHEMY_ECHO'] is True
        assert app.config['TESTING'] is True
        if 'TRAVIS' not in os.environ:
            assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

    def test_production_settings(self):
        """ Tests if the production config loads correctly """

        os.environ['YOURAPPLICATION_MODE'] = 'PRODUCTION'
        app = create_app()

        assert app.config['DEBUG'] is False
        assert app.config['TESTING'] is False
