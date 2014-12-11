#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import pymongo
from tornado import gen
from tornado.web import asynchronous

from laishime.views import BaseHandler


class TopicTweets(BaseHandler):

    @asynchronous
    def get(self, url):
        router = {
            'index.html': self.index_page,
            'last-update-topics': self.get_last_update_topics,
            'most-post-topics': self.get_most_post_topics
        }
        router.get(url, self.redirect_404)()

    def index_page(self):
        self.render('topic_tweets.html')
        self.finish()

    @gen.coroutine
    def get_last_update_topics(self):
        """
        {'topic': '', 'timestamp': ''}
        """
        n_topics = int(self.get_argument('n_topics', 5))
        tweets = self.db.twitter.tweets
        last_update_topics = []
        topics = []

        cursor = tweets.find({'topics': {'$ne': []}},
                             {'topics': 1, 'timestamp': 1}).\
            sort([('timestamp', pymongo.DESCENDING)])

        for docu in (yield cursor.to_list(length=n_topics * 10)):
            docu = cursor.next_object()
            for topic in docu['topics']:
                if topic not in topics:
                    topics.append(topic)
                    last_update_topics.append({
                        'topic': topic,
                        'timestamp': str(docu['timestamp'])
                    })

                if len(topics) >= n_topics:
                    break

            if len(topics) >= n_topics:
                break

        self.write(json.dumps(last_update_topics))
        self.finish()

    def get_most_post_topics(self):
        pass
