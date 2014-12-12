#!/usr/bin/env python
# -*- coding: utf-8 -*-
from laishime.views import BaseHandler
'from tweepy import API, OAuthHandler',
 "auth = OAuthHandler('S6EDKLg7WmZsHVnGxBFFIA', 'oeDkQFBAhTioFNXurRB6UR7Np4N7AORpfuXvbho')",
 'auth_url = auth.get_authorization_url()',
 'auth_url',
 "access_token = auth.get_access_token('h4kGoA0PSBNpUMkhUWbAEIm7CfgLarL7')",
 'access_token',
 'api = API(auth)',
 "s = api.update_status('test')",