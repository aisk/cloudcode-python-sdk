# coding: utf-8

import os


__author__ = 'asaka <lan@leancloud.rocks>'

APP_ID = os.environ.get('APP_ID')
APP_KEY = os.environ.get('APP_KEY')
MASTER_KEY = os.environ.get('MASTER_KEY')


class CloudCodeMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)
