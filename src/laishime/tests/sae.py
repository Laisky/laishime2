#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tornado.wsgi


def create_wsgi_app(app):
    return tornado.wsgi.WSGIAdapter(app)
