# coding: utf-8

from werkzeug.wrappers import Request

import context
from .authorization import AuthorizationMiddleware
from .cloudcode import CloudCodeApplication
from .cloudcode import register_cloud_func
from .cloudcode import register_cloud_hook
from .cloudcode import user

__author__ = 'asaka <lan@leancloud.rocks>'


def wrap(app):
    cloud_app = context.local_manager.make_middleware(AuthorizationMiddleware(CloudCodeApplication()))

    def fn(environ, start_response):
        request = Request(environ)
        if request.path.startswith('/1/functions') or request.path.startswith('/1.1/functions'):
            return cloud_app(environ, start_response)
        return app(environ, start_response)

    return fn


__all__ = [
    'wrap',
    'user',
    'register_cloud_func',
    'register_cloud_hook',
    'local',
]
