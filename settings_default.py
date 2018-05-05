import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """

    """
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Development(Config):
    """

    """
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    USER_SETTINGS_EXIST = True
    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')


class Testing(Config):
    """

    """
    TESTING = True
    SQLALCHEMY_ECHO = True
    if 'TRAVIS' in os.environ:

        if 'SECRET_KEY' in os.environ:
            SECRET_KEY = os.getenv('SECRET_KEY')
        else:
            print('SECRET_KEY is missing.')


class Production(Config):
    """

    """
    USER_SETTINGS_EXIST = True
    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        SQLALCHEMY_DATABASE_URI = os.environ['SQLALCHEMY_DATABASE_URI']
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
