# coding=utf-8
SQLALCHEMY_DATABASE_URI = 'sqlite://'
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAKO_TRANSLATE_EXCEPTIONS = False
BOOK_DIR = None
HOST = '0.0.0.0'
PORT = 8080
DEBUG = False

try:
    from local_settings import *  # noqa
except ImportError:
    pass
