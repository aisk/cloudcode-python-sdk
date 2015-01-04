# coding: utf-8

import os
import hashlib

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException


__author__ = 'asaka <lan@leancloud.rocks>'

APP_ID = os.environ.get('APP_ID')
APP_KEY = os.environ.get('APP_KEY')
MASTER_KEY = os.environ.get('MASTER_KEY')


def sign_by_key(timestamp, key):
    return hashlib.md5('{}{}'.format(timestamp, key)).hexdigest()


class AuthInfoMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        self.parse_header(environ)
        return self.app(environ, start_response)

    def parse_header(self, environ):
        request = Request(environ)
        app_id = request.headers.get('x-avoscloud-application-id') or request.headers.get('x-uluru-application-id')
        app_key = request.headers.get('x-avoscloud-application-key') or request.headers.get('x-uluru-application-key')
        session_token = request.headers.get('x-uluru-session-token') or request.headers.get('x-avoscloud-session-token')
        if app_key is None:
            request_sign = request.headers.get('x-avoscloud-request-sign')
            if request_sign:
                request_sign = request_sign.split(',') if request_sign else []
                sign = request_sign[0].lower()
                timestamp = request_sign[1]
                key = MASTER_KEY if len(request_sign) == 3 and request_sign[2] == 'master' else APP_KEY
                if sign == sign_by_key(timestamp, key):
                    app_key = key

        environ['_app_params'] = {
            'id': app_id,
            'key': app_key,
            'session_token': session_token,
        }


class AuthorizationMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        unauth_response = Response('Unauthorized.', status=401, mimetype='application/json')
        app_params = environ['_app_params']
        if app_params['id'] is None:
            return unauth_response(environ, start_response)


class CloudCodeMiddleware(object):
    def __init__(self, app):
        self.app = app
        self.url_map = Map([
            Rule('/'),
        ])

    def __call__(self, environ, start_response):
        request = Request(environ)
        return self.app(environ, start_response)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        print endpoint, values


def wrap(app):
    return AuthInfoMiddleware(
        AuthInfoMiddleware(
            CloudCodeMiddleware(
                app
            )
        )
    )
