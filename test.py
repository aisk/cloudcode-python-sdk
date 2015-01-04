# coding: utf-8

import requests
from wsgi_intercept import requests_intercept, add_wsgi_intercept


import middleware
from middleware import wrap


__author__ = 'asaka <lan@leancloud.rocks>'

env = None


def app(environ, start_response):
    global env
    env = environ
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello LeanCloud']


def make_app():
    return wrap(app)


host, port = 'localhost', 80
url = 'http://{0}:{1}/'.format(host, port)


def setup():
    global env
    env = None

    middleware.APP_ID = 'mdx1l0uh1p08tdpsk8ffn4uxjh2bbhl86rebrk3muph08qx7'
    middleware.APP_KEY = 'n35a5fdhawz56y24pjn3u9d5zp9r1nhpebrxyyu359cq0ddo'
    middleware.MASTER_KEY = 'h2ln3ffyfzysxmkl4p3ja7ih0y6sq5knsa2j0qnm1blk2rn2'

    requests_intercept.install()
    add_wsgi_intercept(host, port, make_app)


def teardown():
    requests_intercept.uninstall()


def test_origin_response():
    resp = requests.get(url)
    assert resp.ok
    assert resp.content == 'Hello LeanCloud'


def test_app_params_1():
    resp = requests.get(url)
    assert resp.ok
    assert '_app_params' in env


def test_app_params_2():
    resp = requests.get(url, headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
        'x-avoscloud-session-token': 'baz',
    })
    assert resp.ok
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] == 'bar'
    assert env['_app_params']['session_token'] == 'baz'


def test_app_params_3():
    requests.get(url, headers={
        'x-avoscloud-request-sign': '28ad0513f8788d58bb0f7caa0af23400,1389085779854'
    })
    assert env['_app_params']['key'] == 'n35a5fdhawz56y24pjn3u9d5zp9r1nhpebrxyyu359cq0ddo'


def test_app_paramas_4():
    requests.get(url, headers={
        'x-avoscloud-request-sign': 'c884fe684c17c972eb4e33bc8b29cb5b,1389085779854,master'
    })
    assert env['_app_params']['key'] == 'h2ln3ffyfzysxmkl4p3ja7ih0y6sq5knsa2j0qnm1blk2rn2'

