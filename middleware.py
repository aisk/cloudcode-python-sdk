# coding: utf-8

import os
import json
import hashlib

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import NotAcceptable


__author__ = 'asaka <lan@leancloud.rocks>'


ENABLE_TEST = False  # when set to True, every request's environ will stored in `current_environ`, just for test
current_environ = None

APP_ID = os.environ.get('APP_ID')
APP_KEY = os.environ.get('APP_KEY')
MASTER_KEY = os.environ.get('MASTER_KEY')


def sign_by_key(timestamp, key):
    return hashlib.md5('{}{}'.format(timestamp, key)).hexdigest()


class AuthInfoMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if ENABLE_TEST:
            global current_environ
            current_environ = environ
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
                # TODO: check timestamp
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
        if (APP_ID == app_params['id']) and (app_params['key'] in [MASTER_KEY, APP_KEY]):
            return self.app(environ, start_response)

        return unauth_response(environ, start_response)


class CloudCodeMiddleware(object):
    def __init__(self, app):
        self.app = app

        self.url_map = Map([
            Rule('/1/', endpoint='index'),
            Rule('/1.1/', endpoint='index'),
            Rule('/1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1.1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1.1/<class_name>/<hook_name>', endpoint='cloud_hook'),
        ])

    def __call__(self, environ, start_response):
        request = Request(environ)

        try:
            self.dispatch_request(request)
        except HTTPException, e:
            return e(environ, start_response)

        return self.app(environ, start_response)

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        assert isinstance(request, Request)
        params = request.get_data()
        values['params'] = json.loads(params) if params != '' else None
        if endpoint == 'cloud_function':
            dispatch_cloud_func(**values)
        if endpoint == 'cloud_func':
            dispatch_cloud_hook(**values)


def wrap(app):
    return AuthInfoMiddleware(
        AuthorizationMiddleware(
            CloudCodeMiddleware(
                app
            )
        )
    )


_cloud_func_map = {}


def register_cloud_func(func):
    func_name = func.__name__
    if func_name in _cloud_func_map:
        raise RuntimeError('cloud function: {} is already registered'.format(func_name))
    _cloud_func_map[func_name] = func


def dispatch_cloud_func(func_name, params):
    func = _cloud_func_map.get(func_name)
    if not func:
        raise NotFound('xxx')

    print "{} is called!".format(func_name)  # TODO

    func(params)


_cloud_hook_map = {
    'beforeSave': {},
    'afterSave': {},
    'afterUpdate': {},
    'beforeDelete': {},
    'afterDelete': {},
}


def _register_cloud_hook(class_name, hook_name, func):
    if hook_name not in _cloud_hook_map:
        raise RuntimeError('invalid hook name')

    if class_name in _cloud_hook_map[hook_name]:
        raise RuntimeError('cloud hook {} on class {} is already registered'.format(hook_name, class_name))

    _cloud_hook_map[hook_name][class_name] = func


def dispatch_cloud_hook(class_name, hook_name, params):
    if hook_name not in _cloud_hook_map:
        raise NotAcceptable

    print "{}:{} is called!".format(class_name, hook_name)  # TODO

    func = _cloud_hook_map[hook_name].get(class_name)
    if not func:
        raise NotFound
