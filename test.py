# coding: utf-8

import requests
from wsgi_intercept import requests_intercept, add_wsgi_intercept


from middleware import wrap


def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello LeanCloud']


def make_app():
    return wrap(app)


host, port = 'localhost', 80
url = 'http://{0}:{1}/'.format(host, port)


def setup():
    requests_intercept.install()
    add_wsgi_intercept(host, port, make_app)


def teardown():
    requests_intercept.uninstall()


def test_origin_response():
    resp = requests.get(url)
    assert resp.ok
    assert resp.content == 'Hello LeanCloud'
