#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import Counter

import pymongo
from tornado import gen
from tornado.web import asynchronous

from laishime.views import BaseHandler


log = logging.getLogger(__name__)


class TopicTweets(BaseHandler):

    @asynchronous
    def get(self, url):
        router = {
            'index.html': self.index_page,
            'last-update-topics': self.get_last_update_topics,
            'most-post-topics': self.get_most_post_topics
        }
        router.get(url, self.redirect_404)()

    @gen.coroutine
    def index_page(self):
        log.info('index_page')

        tweets = self.db.twitter.tweets
        cursor = tweets.find({}, {'text': 1}).\
            sort([{'timestamp', pymongo.DESCENDING}])
        articles = []

        for docu in (yield cursor.to_list(length=20)):
            articles.append(docu['text'])

        articles = '<p>' + '</p><p>'.join(articles) + '</p>'

        self.render('topic_tweets.html', articles=articles)
        self.finish()

    @gen.coroutine
    def get_last_update_topics(self):
        """
        {'topic': '', 'timestamp': ''}
        """
        log.info('get_last_update_topics')

        n_topics = int(self.get_argument('n_topics', 5))
        tweets = self.db.twitter.tweets
        last_update_topics = []
        topics = []

        cursor = tweets.find({'topics': {'$ne': []}},
                             {'topics': 1, 'timestamp': 1}).\
            sort([('timestamp', pymongo.DESCENDING)])

        for docu in (yield cursor.to_list(length=n_topics * 2)):
            for topic in docu['topics']:
                if topic not in topics:
                    topics.append(topic)
                    last_update_topics.append(
                        {'topic': topic, 'timestamp': str(docu['timestamp'])}
                    )

                if len(topics) >= n_topics:
                    break

            if len(topics) >= n_topics:
                break

        self.write_json(data=last_update_topics)
        self.finish()

    @gen.coroutine
    def get_most_post_topics(self):
        log.info('get_most_post_topics')

        n_topics = int(self.get_argument('n_topics', 5))
        statistics = self.db.twitter.statistics
        most_post_topics = []

        docu = yield statistics.find_one({'collection': 'tweets'})

        topics = Counter(docu['topics_count']).most_common()[: n_topics]
        for (topic, n) in topics:
            most_post_topics.append(
                {'topic': topic, 'count': n}
            )

        self.write_json(data=most_post_topics)
        self.finish()
