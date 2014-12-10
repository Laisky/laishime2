#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.web import asynchronous

from laishime.views import BaseHandler


class TopicTweets(BaseHandler):

    @asynchronous
    def get(self, url):
        router = {
            'index.html': self.index_page
        }
        router.get(url, self.redirect_404)()

    def index_page(self):
        self.render('topic_tweets.html')
        self.finish()
