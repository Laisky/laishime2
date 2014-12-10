#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

from tornado.web import asynchronous

from laishime.views import BaseHandler, DBMixin


class TopicTweets(BaseHandler, DBMixin):

    @asynchronous
    def get(self, url):
        router = {
            'index.html': self.index_page,
            'last-update-topics': self.get_last_update_topics
        }
        router.get(url, self.redirect_404)()

    def index_page(self):
        self.render('topic_tweets.html')
        self.finish()

    def get_last_update_topics(self):
        """
        {'topic': '', 'timestamp': ''}
        """
        tweets = self.conn.twitter.tweets
        last_update_topics = []
        docus = tweets.find(
            {'topics': {'$ne': []}},
            {'topics': 1, 'timestamp': 1}
        ).sort('timestamp', -1)
        topics = []
        for docu in docus:
            for t in docu['topics']:
                if t not in topics:
                    topics.append(t)
                    last_update_topics.append(
                        {'topic': t,
                         'timestamp': str(docu['timestamp'])}
                    )

                if len(topics) == 5:
                    self.write(json.dumps(last_update_topics))
                    self.finish()
                    return
