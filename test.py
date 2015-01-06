# coding: utf-8

import requests
from wsgi_intercept import requests_intercept, add_wsgi_intercept


import middleware
from middleware import wrap


__author__ = 'asaka <lan@leancloud.rocks>'

env = None

TEST_APP_ID = 'mdx1l0uh1p08tdpsk8ffn4uxjh2bbhl86rebrk3muph08qx7'
TEST_APP_KEY = 'n35a5fdhawz56y24pjn3u9d5zp9r1nhpebrxyyu359cq0ddo'
TEST_MASTER_KEY = 'h2ln3ffyfzysxmkl4p3ja7ih0y6sq5knsa2j0qnm1blk2rn2'

NORMAL_HEADERS = {
    'x-avoscloud-application-id': TEST_APP_ID,
    'x-avoscloud-application-key': TEST_APP_KEY,
}


def app(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello LeanCloud']


def make_app():
    return wrap(app)


host, port = 'localhost', 80
url = 'http://{0}:{1}/'.format(host, port)


def setup():
    middleware._ENABLE_TEST = True
    middleware.APP_ID = TEST_APP_ID
    middleware.APP_KEY = TEST_APP_KEY
    middleware.MASTER_KEY = TEST_MASTER_KEY

    requests_intercept.install()
    add_wsgi_intercept(host, port, make_app)


def teardown():
    requests_intercept.uninstall()


# def test_origin_response():
#     resp = requests.get(url)
#     assert resp.ok
#     assert resp.content == 'Hello LeanCloud'


def test_app_params_1():
    requests.get(url)
    assert '_app_params' in middleware.current_environ


def test_app_params_2():
    resp = requests.get(url, headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
        'x-avoscloud-session-token': 'baz',
    })
    env = middleware.current_environ
    assert env['_app_params']['id'] == 'foo'
    assert env['_app_params']['key'] == 'bar'
    assert env['_app_params']['session_token'] == 'baz'


def test_app_params_3():
    requests.get(url, headers={
        'x-avoscloud-request-sign': '28ad0513f8788d58bb0f7caa0af23400,1389085779854'
    })
    env = middleware.current_environ
    assert env['_app_params']['key'] == 'n35a5fdhawz56y24pjn3u9d5zp9r1nhpebrxyyu359cq0ddo'


def test_app_paramas_4():
    requests.get(url, headers={
        'x-avoscloud-request-sign': 'c884fe684c17c972eb4e33bc8b29cb5b,1389085779854,master'
    })
    env = middleware.current_environ
    assert env['_app_params']['key'] == 'h2ln3ffyfzysxmkl4p3ja7ih0y6sq5knsa2j0qnm1blk2rn2'


def test_authorization_1():
    response = requests.get(url + '1.1/', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    })
    assert response.ok


def test_authorization_2():
    response = requests.get(url + '1.1/', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_MASTER_KEY,
    })
    assert response.ok


def test_authorization_3():
    response = requests.get(url + '1.1/', headers={
        'x-avoscloud-application-id': 'foo',
        'x-avoscloud-application-key': 'bar',
    })
    assert response.status_code == 401


def test_register_cloud_func():
    @middleware.register_cloud_func
    def ping(params):
        assert params == {"foo": ["bar", "baz"]}
        return 'pong'

    response = requests.post(url + '/1.1/functions/ping', headers={
        'x-avoscloud-application-id': TEST_APP_ID,
        'x-avoscloud-application-key': TEST_APP_KEY,
    }, json={'foo': ['bar', 'baz']})
    assert response.ok
    assert response.content == 'pong'
