#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
from datetime import datetime
import logging
from collections import Counter

import pymongo
from tornado import gen
from tornado.web import asynchronous
from tweepy import API, OAuthHandler

from laishime.views import BaseHandler


log = logging.getLogger(__name__)


class TopicTweets(BaseHandler):
    _default_n_tweets = 50
    _default_n_topics = 5

    @asynchronous
    def get(self, url):
        log.info('TopicTweets from {}'.format(self.ip))
        router = {
            'index.html': self.index_page,
            'get-last-update-topics': self.get_last_update_topics,
            'get-most-post-topics': self.get_most_post_topics,
            'get-tweets-by-topic': self.get_tweets_by_topic,
            'crawler-tweets': self.crawler_tweets
        }
        router.get(url, self.redirect_404)()

    @gen.coroutine
    def index_page(self):
        log.debug('index_page')

        try:
            tweets = self.db.twitter.tweets
            articles = []

            cursor = tweets.find({}, {'text': 1}).\
                sort([('timestamp', pymongo.DESCENDING)]).\
                limit(self._default_n_tweets)

            while (yield cursor.fetch_next):
                docu = cursor.next_object()
                articles.append(docu['text'])

            articles = '<p>' + '</p><p>'.join(articles) + '</p>'
            self.render('topic_tweets.html', articles=articles)
        except:
            log.error(traceback.format_exc())
        finally:
            self.finish()

    @gen.coroutine
    def get_tweets_by_topic(self):
        log.debug('get_tweets_by_topic')

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
        except:
            log.error(traceback.format_exc())
        finally:
            self.finish()

    @gen.coroutine
    def get_last_update_topics(self):
        """
        {'topic': '', 'timestamp': ''}
        """
        log.debug('get_last_update_topics')

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
        except:
            log.error(traceback.format_exc())
        finally:
            self.finish()

    @gen.coroutine
    def get_most_post_topics(self):
        log.debug('get_most_post_topics')

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
                    """<li title="{:2d}">{}</li>"""
                    .format(n, topic)
                )

            self.write_json(data=most_post_topics)
        except:
            log.error(traceback.format_exc())
        finally:
            self.finish()

    @gen.coroutine
    def crawler_tweets(self):
        log.debug('crawler_tweets')

        try:
            account = self.db.twitter.account
            tweets = self.db.twitter.tweets
            uid = 105351466
            auth = OAuthHandler(
                'S6EDKLg7WmZsHVnGxBFFIA',
                'oeDkQFBAhTioFNXurRB6UR7Np4N7AORpfuXvbho'
            )
            last_stored_tweet = yield tweets.find_one(
                sort=[('id', pymongo.DESCENDING)]
            )
            user_info = yield account.find_one({'id': uid})

            auth.set_access_token(
                user_info['access_token'],
                user_info['access_token_secret']
            )
            api = API(auth)
            #TODO: block!!!
            statuses = api.user_timeline(since_id=last_stored_tweet['id'])

            for status in statuses:
                tweet = status._json
                if tweet['id'] <= last_stored_tweet['id']:
                    continue

                tweet['created_at'] = datetime.strptime(
                    tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y'
                )

                yield tweets.update(
                    {'id': tweets['id']}, tweet, upsert=True
                )
        except:
            log.error(traceback.format_exc())
        finally:
            self.finish()
