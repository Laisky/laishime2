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
def load_authorization(filename):
    """load_authorization reads plain authorization YAML without Python constructors."""
    with open(filename) as stream:
        return yaml.safe_load(stream)


AUTHORIZE = load_authorization(os.path.join(CWD, 'config/authorize.yml'))
TWITTER_AUTH = AUTHORIZE['twitter']

# regex
url_regex = re.compile(
    r"""((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)"""
)

# test
# DB_HOST = 'laisky.com'
