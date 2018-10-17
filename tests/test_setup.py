import os
from app import create_app


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class TestConfiguration:
    def test_create_app_development(self):
        """
        Tests if the app starts correctly.
        """

        os.environ['YOURAPPLICATION_MODE'] = 'DEVELOPMENT'

        app = create_app()
        assert app.config['TESTING'] == False
        assert app.config['DEBUG'] is True
        assert app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] is False
        assert app.config['USER_SETTINGS_EXIST'] is True
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
    def test_create_app_testing(self):
        """
        Tests if the app starts correctly.
        """

        os.environ['YOURAPPLICATION_MODE'] = 'TESTING'
        if 'SQLALCHEMY_DATABASE_URI' in os.environ:
            del os.environ['SQLALCHEMY_DATABASE_URI']

        app = create_app()
        assert app.config['TESTING'] == True
        assert app.config['DEBUG'] is False
        assert app.config['SQLALCHEMY_ECHO'] == True
        if 'TRAVIS' not in os.environ:
            assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False

    def test_create_app_production(self):
        """
        Tests if the app starts correctly.
        """
        os.environ['YOURAPPLICATION_MODE'] = 'PRODUCTION'
        app = create_app()

        assert app.config['USER_SETTINGS_EXIST'] is True
        assert app.config['TESTING'] == False
        assert app.config['DEBUG'] is False
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False
