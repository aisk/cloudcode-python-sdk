# coding: utf-8

import bottle
import cloudcode
from werkzeug.serving import run_simple

__author__ = 'asaka'


@bottle.route('/')
def index():
    return 'Hello LeanCloud!'


@cloudcode.register_cloud_func
def add(params):
    return params['x'] + params['y']

app = bottle.default_app()
app = cloudcode.wrap(app)

if __name__ == '__main__':
    run_simple('localhost', 5000, app)
