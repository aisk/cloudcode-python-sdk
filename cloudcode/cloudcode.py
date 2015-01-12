# coding: utf-8

import json
import logging
import traceback

import leancloud
from werkzeug.wrappers import Request
from werkzeug.wrappers import Response
from werkzeug.routing import Map
from werkzeug.routing import Rule
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from werkzeug.exceptions import NotAcceptable

from . import context


__author__ = 'asaka <lan@leancloud.rocks>'

logger = logging.getLogger('leancloud.cloudcode.cloudcode')

user = context.local('user')


class CloudCodeError(Exception):
    pass


class CloudCodeApplication(object):
    def __init__(self):
        self.url_map = Map([
            # Rule('/1/', endpoint='index'),
            # Rule('/1.1/', endpoint='index'),
            Rule('/1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1.1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1.1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1/onVerified/<verify_type>', endpoint='on_verified'),
            Rule('/1.1/onVerified/<verify_type>', endpoint='on_verified'),
        ])

    def __call__(self, environ, start_response):
        self.process_session(environ)
        request = Request(environ)

        response = self.dispatch_request(request)

        return response(environ, start_response)

    @classmethod
    def process_session(cls, environ):
        if environ['_app_params']['session_token'] in (None, ''):
            context.local.user = None
            return

        session_token = environ['_app_params']['session_token']
        user = leancloud.Object.create('_User', session_token=session_token)
        # TODO: fetch user
        context.local.user = user

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
        except HTTPException, e:
            return e

        params = request.get_data()
        values['params'] = json.loads(params) if params != '' else None

        try:
            if endpoint == 'cloud_function':
                result = dispatch_cloud_func(**values)
            elif endpoint == 'cloud_func':
                result = dispatch_cloud_hook(**values)
            elif endpoint == 'on_verified':
                result = dispatch_on_verified(**values)
            else:
                raise ValueError    # impossible
            return Response(json.dumps({'result': result}), mimetype='application/json')
        except Exception:
            traceback.print_exc()
            # TODO: output the error message in debug mode
            return Response(
                json.dumps({'code': 141, 'error': 'Cloud Code script had an error.'}),
                status=500,
                mimetype='application/json'
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
        raise NotFound('xxx')  # TODO

    logger.info("{} is called!".format(func_name))

    return func(params)


_cloud_hook_map = {
    'beforeSave': {},
    'afterSave': {},
    'afterUpdate': {},
    'beforeDelete': {},
    'afterDelete': {},
}


def register_cloud_hook(class_name, hook_name):
    # hack the hook name
    hook_name = {
        'before_save': 'beforeSave',
        'after_save': 'afterSave',
        'after_update': 'afterUpdate',
        'before_delete': 'beforeDelete',
        'after_delete': 'afterDelete',
    }.get(hook_name) or hook_name

    if hook_name not in _cloud_hook_map:
        raise RuntimeError('invalid hook name: {}'.format(hook_name))

    if class_name in _cloud_hook_map[hook_name]:
        raise RuntimeError('cloud hook {} on class {} is already registered'.format(hook_name, class_name))

    def new_func(func):
        _cloud_hook_map[hook_name][class_name] = func

    return new_func


def dispatch_cloud_hook(class_name, hook_name, params):
    if hook_name not in _cloud_hook_map:
        raise NotAcceptable

    obj = leancloud.Object.create(class_name)

    logger.info("{}:{} is called!".format(class_name, hook_name))

    func = _cloud_hook_map[hook_name].get(class_name)
    if not func:
        raise NotFound

    return func(obj)


_on_verified_map = {}


def register_on_verified(verify_type):
    if verify_type not in {'sms', 'email'}:
        raise RuntimeError('verify_type must be sms or email')

    def new_func(func):
        if verify_type in _on_verified_map:
            raise RuntimeError('on verified is already registered')
        _on_verified_map[verify_type] = func
    return new_func


def dispatch_on_verified(verify_type, user):
    # TODO: parse user
    func = _on_verified_map.get(verify_type)
    if not func:
        return

    return func(user)
