# coding: utf-8

from werkzeug.serving import run_simple

import cloudcode
from flask import Flask


__author__ = 'asaka'


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello LeanCloud!'


@cloudcode.register_cloud_func
def add(params):
    return params['x'] + params['y']


if __name__ == '__main__':
    wsgi_func = cloudcode.wrap(app.wsgi_app)
    run_simple('localhost', 5000, wsgi_func)
