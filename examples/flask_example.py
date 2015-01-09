# coding: utf-8

import cloudcode
from cloudcode import CloudCodeError
from flask import Flask


__author__ = 'asaka'


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello LeanCloud!'


@cloudcode.cloud_func
def add(params):
    user = cloudcode.user
    return params['x'] + params['y']


@cloudcode.cloud_hook('Album', 'before_save')
def before_album_save(obj):
    user = cloudcode.user
    # raise CloudCodeError to prevent save
    return 'ok'


if __name__ == '__main__':
    wsgi_func = cloudcode.wrap(app.wsgi_app)
    cloudcode.run('localhost', 5000, wsgi_func)
