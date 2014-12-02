#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

import tornado.wsgi
import tornado.web
import tornado.gen
try:
    import sae
except ImportError:
    from laishime.tests import sae

from laishime.const import PWD


class Application(tornado.wsgi.WSGIApplication):
    pass


settings = {
    "static_path": os.path.join(PWD, "static"),
    "cookie_secret": "XmuwPAt8wHdnik4Xvc3GXmbXLifVmPZYhoc9Tx4x1iZ",
    "login_url": "/login",
    "xsrf_cookies": True,
    "autoescape": None,
}

app = tornado.wsgi.WSGIApplication(
    [
        (r"/(apple-touch-icon\.png)", tornado.web.StaticFileHandler,
            dict(path=settings['static_path'])),
        (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
            dict(path=settings['static_path']))
    ],
    **settings
)

application = sae.create_wsgi_app(app)
