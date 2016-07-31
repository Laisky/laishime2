#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import logging
from multiprocessing.pool import ThreadPool

from ..const import LOG_NAME, LOG_LEVEL, LOG_PATH
from .tornado import BaseHandler, BackgroundMixin, debug_wrapper
from .parser import twitter_api_parser


__all__ = ['BaseHandler',
           'setup_log', 'BackgroundMixin',
           'twitter_api_parser', 'debug_wrapper']


log = logging.getLogger(LOG_NAME)
_workers = ThreadPool(10)


def setup_log():
    _format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(_format)
    # set stdout
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(LOG_LEVEL)
    ch.setFormatter(formatter)
    # set log file
    fh = logging.FileHandler(LOG_PATH)
    fh.setLevel(LOG_LEVEL)
    fh.setFormatter(formatter)
    # log
    log = logging.getLogger(LOG_NAME)
    # log.addHandler(ch)
    # log.addHandler(fh)
