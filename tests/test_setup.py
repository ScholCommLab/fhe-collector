import os
from app import create_app


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


class TestConfiguration:
    def test_create_app_development(self):
        """
        Tests if the app starts correctly.
        """

        os.environ['ENV'] = 'development'
        app = create_app()

        assert app.config['TESTING'] is False
        assert app.config['DEBUG'] is True
        assert app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] is False
        assert app.config['USER_SETTINGS_EXIST'] is True
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

    def test_create_app_testing(self):
        """
        Tests if the app starts correctly.
        """

        os.environ['ENV'] = 'testing'
        if 'SQLALCHEMY_DATABASE_URI' in os.environ:
            del os.environ['SQLALCHEMY_DATABASE_URI']
        app = create_app()

        assert app.config['TESTING'] is True
        assert app.config['DEBUG'] is False
        assert app.config['SQLALCHEMY_ECHO'] is True
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False

    def test_create_app_production(self):
        """
        Tests if the app starts correctly.
        """
        os.environ['ENV'] = 'production'
        app = create_app()

        assert app.config['USER_SETTINGS_EXIST'] is True
        assert app.config['TESTING'] is False
        assert app.config['DEBUG'] is False
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False
