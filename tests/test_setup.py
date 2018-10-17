import os
from app import create_app


BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


class TestConfiguration:
    def test_create_app(self):
        """
        Tests if the app starts correctly.
        """
        app = create_app()
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] == False

        if os.environ['YOURAPPLICATION_MODE'] == 'DEVELOPMENT':
            assert app.config['TESTING'] == False
            assert app.config['DEBUG'] is True
            assert app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] is True
            assert app.config['USER_SETTINGS_EXIST'] is True
            assert app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql://localhost/fhe_collector'
        elif os.environ['YOURAPPLICATION_MODE'] == 'TESTING':
            assert app.config['TESTING'] == True
            assert app.config['DEBUG'] is False
            assert app.config['SQLALCHEMY_ECHO'] == True
            if 'TRAVIS' not in os.environ:
                assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        elif os.environ['YOURAPPLICATION_MODE'] == 'PRODUCTION':
            assert app.config['USER_SETTINGS_EXIST'] is True
            assert app.config['TESTING'] == False
            assert app.config['DEBUG'] is True
