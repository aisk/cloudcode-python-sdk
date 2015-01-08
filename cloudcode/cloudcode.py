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


class CloudCodeApplication(object):
    def __init__(self):
        self.url_map = Map([
            # Rule('/1/', endpoint='index'),
            # Rule('/1.1/', endpoint='index'),
            Rule('/1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1.1/functions/<func_name>', endpoint='cloud_function'),
            Rule('/1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
            Rule('/1.1/functions/<class_name>/<hook_name>', endpoint='cloud_hook'),
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
            if endpoint == 'cloud_func':
                result = dispatch_cloud_hook(**values)
            return Response(json.dumps({'result': result}), mimetype='application/json')
        except Exception:
            traceback.print_exc()
            return Response('internal error', status=500)


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
    # if isinstance(result, basestring):
    #     return Response(result, mimetype='text/plain')
    # if isinstance(result, dict):
    #     return Response(json.dumps(result), mimetype='application/json')
    # if isinstance(result, Response):
    #     return result
    # raise TypeError('invalid cloud function result')


_cloud_hook_map = {
    'beforeSave': {},
    'afterSave': {},
    'afterUpdate': {},
    'beforeDelete': {},
    'afterDelete': {},
}


def register_cloud_hook(class_name, hook_name, func):
    if hook_name not in _cloud_hook_map:
        raise RuntimeError('invalid hook name')

    if class_name in _cloud_hook_map[hook_name]:
        raise RuntimeError('cloud hook {} on class {} is already registered'.format(hook_name, class_name))

    _cloud_hook_map[hook_name][class_name] = func


def dispatch_cloud_hook(class_name, hook_name, params):
    if hook_name not in _cloud_hook_map:
        raise NotAcceptable

    obj = leancloud.Object.create(class_name)

    logger.info("{}:{} is called!".format(class_name, hook_name))

    func = _cloud_hook_map[hook_name].get(class_name)
    if not func:
        raise NotFound

    return func(obj)
    # if isinstance(result, basestring):
    #     return Response(result, mimetype='text/plain')
    # if isinstance(result, dict):
    #     return Response(json.dumps(result), mimetype='application/json')
    # if isinstance(result, Response):
    #     return result
    # raise TypeError('invalid cloud hook result')
