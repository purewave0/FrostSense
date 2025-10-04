import os


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    AUTO_CREATE_ADMIN = True
    AUTO_CREATE_SYSTEM_SETTINGS = True
    REPORTS_DIRECTORY = os.path.join(basedir, 'app', 'generated_reports')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    AUTO_CREATE_ADMIN = False
    AUTO_CREATE_SYSTEM_SETTINGS = False
