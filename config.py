import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    Setting the default environment settings.
    """

    from dotenv import load_dotenv

    load_dotenv()
    FLASK_APP = os.environ.get("FLASK_APP") or "fhe_collector"
    FLASK_ENV = os.environ.get("FLASK_ENV") or "development"
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_TOKEN = os.environ.get("API_TOKEN") or None
    CSV_FILENAME = os.environ.get("CSV_FILENAME") or None
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL") or None
    APP_EMAIL = os.environ.get("APP_EMAIL") or None
    SECRET_KEY = os.environ.get("SECRET_KEY") or None
    NCBI_TOOL = os.environ.get("NCBI_TOOL") or None
    FB_APP_ID = os.environ.get("FB_APP_ID") or None
    FB_APP_SECRET = os.environ.get("FB_APP_SECRET") or None
    FB_HOURLY_RATELIMIT = os.environ.get("FB_HOURLY_RATELIMIT") or 200
    FB_BATCH_SIZE = os.environ.get("FB_BATCH_SIZE") or 50
    URL_BATCH_SIZE = os.environ.get("URL_BATCH_SIZE") or 1000

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """
    Setting the development environment settings.
    Database is sqlite file or a postgresql database string passed by an environment variable.
    """

    FLASK_ENV = os.environ.get("FLASK_ENV") or "development"
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URI") or "postgresql://localhost/fhe_collector_dev"
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        from flask_debugtoolbar import DebugToolbarExtension

        DebugToolbarExtension(app)


class TestingConfig(Config):
    FLASK_ENV = os.environ.get("FLASK_ENV") or "testing"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URI")
        or "postgresql://localhost/fhe_collector_test"
    )

    API_TOKEN = "api-token"
    CSV_FILENAME = "data.csv"
    ADMIN_EMAIL = "admin@fhe.com"
    APP_EMAIL = "app@fhe.com"
    NCBI_TOOL = "FHE Collector"
    FB_APP_ID = "123456789012345"
    FB_APP_SECRET = "0987654321"
    FB_HOURLY_RATELIMIT = 100
    FB_BATCH_SIZE = 20
    URL_BATCH_SIZE = 500


class TravisConfig(TestingConfig):
    """
    Setting the test environment settings.
    """

    TRAVIS = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = (
        "postgresql+psycopg2://postgres@localhost:5432/travis_ci_test"
    )


class ProductionConfig(Config):
    """
    Setting the production environment settings.
    """

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("PROD_DATABASE_URI") or "postgresql://localhost/fhe_collector"
    )
    FLASK_ENV = os.environ.get("FLASK_ENV") or "production"

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
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DOCKER_DATABASE_URI") or "postgresql://localhost/fhe_collector"
    )

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
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DOCKER_COMPOSE_DATABASE_URI")
        or "postgresql://postgres:postgres@localhost/fhe_collector"
    )

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


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "travis": TravisConfig,
    "docker": DockerConfig,
    "docker_compose": DockerComposeConfig,
    "unix": UnixConfig,
    "default": DevelopmentConfig,
}
