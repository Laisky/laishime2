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
    _default_n_tweets = 50
    _default_n_topics = 5

    @asynchronous
    def get(self, url):
        router = {
            'index.html': self.index_page,
            'get-last-update-topics': self.get_last_update_topics,
            'get-most-post-topics': self.get_most_post_topics,
            'get-get-tweets-by-topic': self.get_tweets_by_topic
        }
        router.get(url, self.redirect_404)()

    def index_page(self):
        log.info('index_page from {}'.format(self.ip))

        try:
            tweets = self.db.twitter.tweets
            articles = []

            cursor = tweets.find({}, {'text': 1}).\
                sort([{'timestamp', pymongo.DESCENDING}]).\
                limit(self._default_n_tweets)

            while (yield cursor.fetch_next):
                docu = cursor.next_object()
                articles.append(docu['text'])

            articles = '<p>' + '</p><p>'.join(articles) + '</p>'
            self.render('topic_tweets.html', articles=articles)
            self.finish()
        except Exception as err:
            log.error(err)

    @gen.coroutine
    def get_tweets_by_topic(self):
        log.info('get_tweets_by_topic from {}'.format(self.ip))

        try:
            topic = str(self.get_argument('topic', strip=True))
            tweets = self.db.twitter.tweets
            articles = []
            cursor = tweets.find({'topics': topic}, {'text': 1}).\
                limit(self._default_n_tweets)

            while (yield cursor.fetch_next):
                docu = cursor.next_object()
                articles.append(docu['text'])

            articles = '<p>' + '</p><p>'.join(articles) + '</p>'

            self.write_json(data=articles)
            self.finish()
        except Exception as err:
            log.error(err)

    @gen.coroutine
    def get_last_update_topics(self):
        """
        {'topic': '', 'timestamp': ''}
        """
        log.info('get_last_update_topics from {}'.format(self.ip))

        try:
            n_topics = int(
                self.get_argument('n_topics', self._default_n_topics)
            )
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
                            """<li title="{}">{}</li>"""
                            .format(str(docu['timestamp']), topic)
                        )

                    if len(topics) >= n_topics:
                        break

                if len(topics) >= n_topics:
                    break

            last_update_topics = ''.join(last_update_topics)
            self.write_json(data=last_update_topics)
            self.finish()
        except Exception as err:
            log.error(err)

    @gen.coroutine
    def get_most_post_topics(self):
        log.info('get_most_post_topics from {}'.format(self.ip))

        try:
            n_topics = int(
                self.get_argument('n_topics', self._default_n_topics)
            )
            statistics = self.db.twitter.statistics
            most_post_topics = []

            docu = yield statistics.find_one({'collection': 'tweets'})

            topics = Counter(docu['topics_count']).most_common()[: n_topics]
            for (topic, n) in topics:
                most_post_topics.append(
                    """<li title="{count::2d}">{}</li>"""
                    .format(n, topic)
                )

            self.write_json(data=most_post_topics)
            self.finish()
        except Exception as err:
            log.error(err)
