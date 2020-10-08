import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """
    Setting the default environment settings.
    """

    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Config):
    """
    Setting the development environment settings.
    Database is sqlite file or a postgresql database string passed by an environment variable.
    """

    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    USER_SETTINGS_EXIST = True

    if "SQLALCHEMY_DATABASE_URI" in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "app.db")


class Testing(Config):
    """
    Setting the test environment settings.
    """

    TESTING = True
    SQLALCHEMY_ECHO = True
    # only execute if code is running on travis
    if "TRAVIS" in os.environ:
        NCBI_TOOL = os.getenv("NCBI_TOOL")
        APP_EMAIL = os.getenv("APP_EMAIL")
        FB_APP_ID = os.getenv("FB_APP_ID")
        FB_APP_SECRET = os.getenv("FB_APP_SECRET")
        if "SECRET_KEY" in os.environ:
            SECRET_KEY = os.getenv("SECRET_KEY")
        else:
            print("SECRET_KEY is missing.")
    if "SQLALCHEMY_DATABASE_URI" in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class Production(Config):
    """
    Setting the production environment settings.
    """

    USER_SETTINGS_EXIST = True
    if "SQLALCHEMY_DATABASE_URI" in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "app.db")
