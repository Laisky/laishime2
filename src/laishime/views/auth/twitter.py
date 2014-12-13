#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import yaml
from tweepy import API, OAuthHandler

from laishime.views import BaseHandler
from laishime.const import PWD


CONFIG = yaml.load(
    os.path.join(PWD, 'config', 'authorize.yml')
)


class TwitterCrawler(BaseHandler):
    pass
auth = OAuthHandler(
    'S6EDKLg7WmZsHVnGxBFFIA',
    'oeDkQFBAhTioFNXurRB6UR7Np4N7AORpfuXvbho'
)

# auth_url = auth.get_authorization_url()
# auth_url
# access_token = auth.get_access_token('h4kGoA0PSBNpUMkhUWbAEIm7CfgLarL7')
# access_token
# api = API(auth)
# s = api.update_status('test')
