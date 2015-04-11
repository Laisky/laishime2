#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging
import contextlib
import traceback

import tornado
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from ..status import OK
from ..const import LOG_NAME


log = logging.getLogger(LOG_NAME)


def debug_wrapper(func):
    def wrapper(*args, **kw):
        try:
            yield from func(*args, **kw)
        except Exception:
            log.error(traceback.format_exc())
            raise
    return wrapper


class TemplateRendering():
    """
    A simple class to hold methods for rendering templates.
    Copied from
        http://bibhas.in/blog/\
            using-jinja2-as-the-template-engine-for-tornado-web-framework/
    """
    def render_template(self, template_name, **kwargs):
        template_dirs = []
        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )

        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    @property
    def db(self):
        return self.application.db

    @property
    def ip(self):
        return self.request.headers.get('X-Real-IP', self.request.remote_ip)

    def write_json(self, *, status=OK, msg='', data={}):
        self.write(json.dumps({
            'status': status,
            'msg': msg,
            'data': data
        }))

    def redirect_404(self):
        self.redirect('/404.html')

    def render(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        def static_url(path):
            prefix = self.settings.get('static_url_prefix')
            return os.path.join(prefix, path)

        kwargs.update({
            'settings': self.settings,
            'static_url': static_url,
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)


@contextlib.contextmanager
def trace_in_coroutine():
    try:
        yield
    except Exception:
        log.error("exception in asynchronous operation")


class BackgroundMixin(tornado.web.RequestHandler):
    """
    EXAMPLE:
        # blocking task like querying to MySQL
        def blocking_task(n):
            sleep(n)
            return n

        class Handler(BackgroundMixin):
            @asynchronous
            def get(self):
                self.run_background(blocking_task, self.on_complete, (10,))

            def on_complete(self, res):
                self.write("Test {0}<br/>".format(res))
                self.finish()
    """
    def run_background(self, func, callback, *args, **kw):
        self.ioloop = tornado.ioloop.IOLoop.instance()

        def _callback(result):
            self.ioloop.add_callback(lambda: callback(result))

        _workers.apply_async(func, args, kw, _callback)
