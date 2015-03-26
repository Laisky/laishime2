#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging

from motor import MotorClient
import tornado.wsgi
import tornado.web
from tornado.options import define, options

try:
    import sae
except ImportError:
    from .tests import sae

from .const import PWD
from .views import BaseHandler, TopicTweets


# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)
define('config', default=os.path.join(PWD, 'config', 'server.conf'))
define('port', default=27800, type=int)
define('debug', default=False, type=bool)
define('dbhost', default='127.0.0.1', type=str)
define('dbport', default=27016, type=int)


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
            'debug': options.debug
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
        log.debug('connect dabase at {}:{}'
                  .format(options.dbhost, options.dbport))

        self.db = MotorClient(host=options.dbhost, port=options.dbport)


application = sae.create_wsgi_app(Application())
