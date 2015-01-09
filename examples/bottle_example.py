# coding: utf-8

import bottle
import cloudcode

__author__ = 'asaka'


@bottle.route('/')
def index():
    return 'Hello LeanCloud!'


@cloudcode.cloud_func
def add(params):
    user = cloudcode.user
    return params['x'] + params['y']


@cloudcode.cloud_hook('Album', 'before_save')
def before_album_save(obj):
    user = cloudcode.user
    return 'ok'


app = bottle.default_app()
app = cloudcode.wrap(app)

if __name__ == '__main__':
    cloudcode.run('localhost', 5000, app)
