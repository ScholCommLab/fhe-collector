import os
from pydantic import BaseSettings


ROOT_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))


class BaseConfig(BaseSettings):
    """Setting the default environment settings."""

    SQLALCHEMY_DATABASE_URI: str = ""
    SECRET_KEY: str = ""
    ADMIN_EMAIL: str = ""
    APP_EMAIL: str = ""
    NCBI_TOOL: str = ""
    FB_API_TOKEN: str = ""
    FB_APP_ID: str = ""
    FB_APP_SECRET: str = ""
    FB_HOURLY_RATELIMIT: int = 200
    FB_BATCH_SIZE: int = 50
    URL_BATCH_SIZE: int = 1000
    FLASK_DEBUG: bool = False
    TESTING: bool = False
    TRAVIS: bool = False
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(BaseConfig):
    """Setting the development environment settings.

    Database is sqlite file or a postgresql database string passed by an environment variable.
    """

    FLASK_DEBUG: bool = True
    DEBUG_TB_INTERCEPT_REDIRECTS: bool = False
    FLASK_RUN_EXTRA_FILES: str = "app/templates/"

    class Config:
        env_file = os.path.join(ROOT_DIR, "env/development.env")

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(app)


class TestingConfig(BaseConfig):

    TESTING: bool = True

    class Config:
        env_file = os.path.join(ROOT_DIR, "env/testing.env")

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)


class ProductionConfig(BaseConfig):
    """Setting the production environment settings.
    """

    class Config:
        env_file = os.path.join(ROOT_DIR, "env/production.env")

    @classmethod
    def init_app(cls, app):
        BaseConfig.init_app(app)

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
        env_file = os.path.join(ROOT_DIR, "env/production.env")

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
        env_file = os.path.join(ROOT_DIR, "env/production.env")

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
