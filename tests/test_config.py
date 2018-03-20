import os
from app import create_app


BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


class TestConfig:
    def test_dev_config(self):
        """ Tests if the development config loads correctly """

        app = create_app('config.Development')

        assert app.config['DEBUG'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

    def test_test_config(self):
        """ Tests if the test config loads correctly """

        app = create_app('config.Testing')

        assert app.config['DEBUG'] is True
        assert app.config['SQLALCHEMY_ECHO'] is True
        assert app.config['TESTING'] is True
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

    def test_prod_config(self):
        """ Tests if the production config loads correctly """

        app = create_app('config.Production')

        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'postgresql+psycopg2://root:pass@localhost/fhe'
        assert app.config['DEBUG'] is False
