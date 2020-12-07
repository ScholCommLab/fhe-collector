import os
from pydantic import BaseSettings


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)


class Config(BaseSettings):
    """Setting the default environment settings."""

    SQLALCHEMY_DATABASE_URI: str = ""
    SECRET_KEY: str = ""
    FLASK_DEBUG: bool = False
    DEBUG: bool = False
    TESTING: bool = False
    TRAVIS: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    API_TOKEN: str = ""
    ADMIN_EMAIL: str = ""
    APP_EMAIL: str = ""
    NCBI_TOOL: str = ""
    FB_APP_ID: str = ""
    FB_APP_SECRET: str = ""
    FB_HOURLY_RATELIMIT: int = 200
    FB_BATCH_SIZE: int = 50
    URL_BATCH_SIZE: int = 1000

    class Config:
        env_file = os.path.join(os.path.dirname(BASE_DIR), "env/.env")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Setting the development environment settings.

    Database is sqlite file or a postgresql database string passed by an environment variable.
    """

    FLASK_ENV: str = "development"
    FLASK_DEBUG: bool = True
    DEBUG: bool = True
    DEBUG_TB_INTERCEPT_REDIRECTS: bool = False

    class Config:
        env_file = os.path.join(ROOT_DIR, "env/development.env")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(app)


class TestingConfig(Config):
    FLASK_ENV: str = "testing"
    TESTING: bool = True

    class Config:
        env_file = os.path.join(ROOT_DIR, "env/testing.env")

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class ProductionConfig(Config):
    """Setting the production environment settings.
    """

    FLASK_ENV: str = "production"

    class Config:
        env_file = os.path.join(ROOT_DIR, "env/production.env")

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


class UnixConfig(ProductionConfig):
    class Config:
        env_file = os.path.join(ROOT_DIR, "env/production.env")

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.INFO)
        app.logger.addHandler(syslog_handler)


class DockerConfig(ProductionConfig):
    class Config:
        env_file = os.path.join(ROOT_DIR, "env/docker.env")

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
    class Config:
        env_file = os.path.join(ROOT_DIR, "env/docker.env")

    @classmethod
    def init_app(cls, app):
        DockerConfig.init_app(app)


def get_config_class(config_name="default"):
    configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
        "docker": DockerConfig,
        "docker_compose": DockerComposeConfig,
        "unix": UnixConfig,
        "default": DevelopmentConfig,
    }
    return configs[config_name]
