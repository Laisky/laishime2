#!/usr/bin/env python
# -*- coding: utf-8 -*-
import traceback
import logging
import datetime
from collections import Counter, defaultdict

import pymongo
import tornado
from tornado.web import asynchronous
from tweepy import API, OAuthHandler

from ..utils import BaseHandler, twitter_api_parser, debug_wrapper
from ..const import LOG_NAME, url_regex, TWITTER_AUTH
from ..status import ERROR


log = logging.getLogger(LOG_NAME)


class TopicTweets(BaseHandler):
    _default_n_tweets = 100
    _default_n_topics = 8

    @asynchronous
    def get(self, url):
        log.info('TopicTweets from {}'.format(self.ip))
        router = {
            'index.html': self.index_page,
            'get-last-update-topics': self.get_last_update_topics,
            'get-most-post-topics': self.get_most_post_topics,
            'get-tweets-by-topic': self.get_tweets_by_topic,
            'crawler-tweets': self.crawler_tweets,
            'update-statistics': self.update_statistics
        }
        router.get(url, self.redirect_404)()

    @tornado.gen.coroutine
    def index_page(self):
        log.debug('index_page')

        try:
            tweets = self.db.twitter.tweets
            articles = []

            cursor = tweets.find({}, {'text': 1}).\
                sort([('created_at', pymongo.DESCENDING)]).\
                limit(self._default_n_tweets)

            while (yield cursor.fetch_next):
                docu = cursor.next_object()
                docu['text'] = self._render_url(docu['text'])
                articles.append(docu['text'])

            articles = '<p>' + '</p><p>'.join(articles) + '</p>'
            self.render('topic_tweets.html', articles=articles)
        except:
            log.error(traceback.format_exc())
        finally:
            self.finish()

    def _render_url(self, text):

        for url in url_regex.findall(text):
            url = ''.join([u for u in url if u])
            url_link = '<a href="{url}" target="_blank">{url}</a>'.\
                format(url=url)
            log.debug('replace url from {} to {}'.format(url, url_link))
            text = text.replace(url, url_link)

        return text

    @tornado.gen.coroutine
    @debug_wrapper
    def get_tweets_by_topic(self):
        topic = str(self.get_argument('topic', strip=True))
        log.debug('get_tweets_by_topic for topic {}'.format(topic))

        tweets = self.db.twitter.tweets
        articles = []
        cursor = tweets.find({'topics': topic}, {'text': 1}) \
            .sort([('created_at', pymongo.ASCENDING)]) \
            .limit(self._default_n_tweets)

        while (yield cursor.fetch_next):
            docu = cursor.next_object()
            docu['text'] = self._render_url(docu['text'])
            articles.append(docu['text'])

        articles = '<p>' + '</p><p>'.join(articles) + '</p>'

        self.write_json(data=articles)
        self.finish()

    @tornado.gen.coroutine
    @debug_wrapper
    def get_last_update_topics(self):
        """
        {'topic': '', 'created_at': ''}
        """
        n_topics = int(
            self.get_argument('n_topics', self._default_n_topics)
        )
        log.debug('get_last_update_topics for n_topics {}'.format(n_topics))

        tweets = self.db.twitter.tweets
        last_update_topics = []
        topics = set()

        cursor = tweets.find({'topics': {'$ne': []}},
                             {'topics': 1, 'created_at': 1}).\
            sort([('created_at', pymongo.DESCENDING)])

        while (yield cursor.fetch_next):
            docu = cursor.next_object()
            for topic in set(docu['topics']) - topics:
                topics.add(topic)
                last_update_topics.append(
                    """<li title="{}">{}</li>"""
                    .format(str(docu['created_at']), topic)
                )

                if len(topics) >= n_topics:
                    break

            if len(topics) >= n_topics:
                break

        last_update_topics = ''.join(last_update_topics)
        self.write_json(data=last_update_topics)
        self.finish()

    @tornado.gen.coroutine
    @debug_wrapper
    def get_most_post_topics(self):
        n_topics = int(
            self.get_argument('n_topics', self._default_n_topics)
        )
        log.debug('get_most_post_topics for n_topics {}'.format(n_topics))

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
        self.finish()

    @tornado.gen.coroutine
    @debug_wrapper
    def update_statistics(self):
        log.debug('update_statistics')

        cursor = self.db.twitter.tweets.find({'topics': {'$ne': []}}) \
            .max_time_ms(None)
        topics = defaultdict(int)

        while (yield cursor.fetch_next):
            docu = cursor.next_object()
            for topic in docu['topics']:
                topics[topic] += 1

        docu = {
            'collection': 'tweets',
            'topics_count': topics,
            'update_at': datetime.datetime.utcnow()
        }
        yield self.db.twitter.statistics.update(
            {'collection': docu['collection']},
            {'$set': docu}
        )
        self.write_json(msg='updated ok')
        self.finish()

    @tornado.gen.coroutine
    def crawler_tweets(self):
        log.debug('crawler_tweets')

        try:
            # TODO modularity!
            account = self.db.twitter.account
            tweets = self.db.twitter.tweets
            uid = 105351466
            auth = OAuthHandler(
                TWITTER_AUTH['CONSUMER_KEY'],
                TWITTER_AUTH['CONSUMER_SECRET']
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
            # TODO: block!!!
            statuses = api.user_timeline(since_id=last_stored_tweet['id'])

            count = 0
            for status in statuses:
                tweet = status._json
                if tweet['id'] <= last_stored_tweet['id']:
                    continue

                tweet = twitter_api_parser(tweet)
                yield tweets.update(
                    {'id': tweet['id']}, {'$set': tweet}, upsert=True
                )
                count += 1
                log.debug('updated {}'.format(tweet['id']))

            self.write_json(data='success crawl {} tweets'.format(count))
        except:
            err = traceback.format_exc()
            log.error(err)
            self.write_json(msg=err, status=ERROR)
        finally:
            self.finish()
