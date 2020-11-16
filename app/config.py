import os
from pydantic import BaseSettings, FilePath


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(BaseSettings):
    """
    Setting the default environment settings.
    """

    FLASK_ENV: str = "development"
    TRAVIS: bool = False
    DEBUG: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    API_TOKEN: str = None
    CSV_FILENAME: FilePath = None
    ADMIN_EMAIL: str = None
    APP_EMAIL: str = None
    SECRET_KEY: str = "my-secret-key"
    NCBI_TOOL: str = None
    FB_APP_ID: str = None
    FB_APP_SECRET: str = None
    FB_HOURLY_RATELIMIT: int = 200
    FB_BATCH_SIZE: int = 50
    URL_BATCH_SIZE: int = 1000

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Setting the development environment settings.
    Database is sqlite file or a postgresql database string passed by an environment variable.
    """

    FLASK_ENV: str = "development"
    DEBUG: bool = True
    DEBUG_TB_INTERCEPT_REDIRECTS: bool = False
    SQLALCHEMY_DATABASE_URI: str = "postgresql://localhost/fhe_collector_dev"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(app)


class TestingConfig(Config):
    TESTING = True
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = "postgresql://localhost/fhe_collector_test"

    class Config:
        env_file = ".env.testing"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class TravisConfig(Config):
    """
    Setting the test environment settings.
    """

    TESTING = True
    DEBUG: bool = False
    TRAVIS = True
    SQLALCHEMY_ECHO: bool = True
    SQLALCHEMY_DATABASE_URI: str = "postgresql+psycopg2://postgres@localhost:5432/travis_ci_test"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    """
    Setting the production environment settings.
    """

    FLASK_ENV: str = "production"
    SQLALCHEMY_DATABASE_URI: str = "postgresql://localhost/fhe_collector"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import RotatingFileHandler

        if not os.path.exists("logs"):
            os.mkdir("logs")

        file_handler = RotatingFileHandler(
            "logs/fhe.log", maxBytes=10240, backupCount=10
        )

        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Facebook Hidden Engagement")


class DockerConfig(ProductionConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql://localhost/fhe_collector"

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


class DockerComposeConfig(DockerConfig):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/fhe_collector"

    @classmethod
    def init_app(cls, app):
        DockerConfig.init_app(app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


def get_config_name():
    return os.getenv("FLASK_CONFIG") or "default"


def get_config(config_name="default"):
    configs = {
        "development": DevelopmentConfig(),
        "testing": TestingConfig(),
        "production": ProductionConfig(),
        "travis": TravisConfig(),
        "docker": DockerConfig(),
        "docker_compose": DockerComposeConfig(),
        "unix": UnixConfig(),
        "default": DevelopmentConfig(),
    }
    return configs[config_name]
