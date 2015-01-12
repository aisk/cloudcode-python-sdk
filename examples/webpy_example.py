# coding: utf-8

import cloudcode
import web


__author__ = 'asaka <lan@leancloud.rocks>'


class Index(object):
    def GET(self):
        return 'Hello LeanCloud!'

urls = (
    '/', 'Index',
)


app = web.application(urls, globals()).wsgifunc()
app = cloudcode.wrap(app)


if __name__ == '__main__':
    cloudcode.run('localhost', 5000, app)
