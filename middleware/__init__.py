# coding: utf-8

from werkzeug.wrappers import Request


__author__ = 'asaka <lan@leancloud.rocks>'


from .authorization import AuthorizationMiddleware
from .cloudcode import CloudCodeApplication
from .cloudcode import register_cloud_func
from .cloudcode import register_cloud_hook


def wrap(app):
    cloud_app = AuthorizationMiddleware(CloudCodeApplication())

    def fn(environ, start_response):
        request = Request(environ)
        if request.path.startswith('/1/functions') or request.path.startswith('/1.1/functions'):
            return cloud_app(environ, start_response)
        return app(environ, start_response)

    return fn


__all__ = [
    'wrap',
    'register_cloud_func',
    'register_cloud_hook',
]
