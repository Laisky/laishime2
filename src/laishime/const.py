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
    r"(?xi)"
    "\b"
    "("                                     # Capture 1: entire matched URL
    "(?:"
    "https?://"                             # http or https protocol
    "|"                                     # or
    "www\d{0,3}[.]"                         # "www.", "www1.", "www2." … "www999."
    "|"                                     # or
    "[a-z0-9.\-]+[.][a-z]{2,4}/"            # looks like domain name followed by a slash
    ")"
    "(?:"                                   # One or more:
    "[^\s()<>]+"                            # Run of non-space, non-()<>
    "|"                                     # or
    "\(([^\s()<>]+|(\([^\s()<>]+\)))*\)"    # balanced parens, up to 2 levels
    ")+"
    "(?:"                                   # End with:
    "\(([^\s()<>]+|(\([^\s()<>]+\)))*\)"    # balanced parens, up to 2 levels
    "|"                                     # or
    "[^\s`!()\[\]{};:'\".,<>?«»\“\”‘’]"     # not a space or one of these punct chars
    ")"
    ")"
)

# test
# DB_HOST = 'laisky.com'
