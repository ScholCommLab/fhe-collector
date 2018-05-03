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
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class Testing(Config):
    """

    """
    TESTING = True
    SQLALCHEMY_ECHO = True
    if os.environ.get('DATABASE_URL') is None:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class Production(Config):
    """

    """
    if os.environ.get('DATABASE_URL'):
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    if os.environ.get('SQLALCHEMY_DATABASE_URI'):
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
