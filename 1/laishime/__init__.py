#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from motor import MotorClient
import tornado.wsgi
import tornado.web
import tornado.options

try:
    import sae
except ImportError:
    from .tests import sae

from .const import PWD
from .views import BaseHandler, TopicTweets


class PageNotFound(BaseHandler):
    def get(self, url=''):
        self.render('404.html', url=url)
        self.finish()


class Application(tornado.wsgi.WSGIApplication):
    def __init__(self):
        settings = {
            'static_path': os.path.join(PWD, 'static'),
            'static_url_prefix': '/static/',
            'template_path': os.path.join(PWD, 'static', 'templates'),
            'cookie_secret': 'XmuwPAt8wHdnik4Xvc3GXmbXLifVmPZYhoc9Tx4x1iZ',
            'login_url': '/login/',
            'xsrf_cookies': True,
            'autoescape': None,
        }
        handlers = [
            # -------------- handler --------------
            ('/404.html', PageNotFound),
            ('/topic_tweets/(.*)', TopicTweets)
        ]
        handlers.append(('/(.*)', PageNotFound))
        super(Application, self).__init__(handlers, **settings)
        self.setup_db()

    def setup_db(self):
        self.db = MotorClient()


application = sae.create_wsgi_app(Application())
