# coding: utf-8

import requests
from wsgi_intercept import requests_intercept, add_wsgi_intercept


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