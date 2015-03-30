#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import logging

import yaml


CWD = os.path.dirname(__file__)

# log
LOG_PATH = '/tmp/laishime.log'
LOG_LEVEL = logging.DEBUG
LOG_NAME = 'laishime'

# authorize
AUTHORIZE = yaml.load(open(os.path.join(CWD, 'config/authorize.yml')))
TWITTER_AUTH = AUTHORIZE['twitter']

# regex
url_regex = re.compile(
    r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)"""
    r"""(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+"""
    r"""(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{}"""
    r""";:'".,<>?«»“”‘’]))"""
)

# test
# DB_HOST = 'laisky.com'
