#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado
from multiprocessing.pool import ThreadPool


_workers = ThreadPool(10)


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
