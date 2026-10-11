"""Offline regressions for the actual tweet write paths and MongoDB drivers."""
import ast
from collections import defaultdict
from concurrent.futures import Future
import datetime
import importlib.util
import logging
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from motor import MotorClient
import pymongo
from tornado.ioloop import IOLoop
from tornado import gen

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mongo_compatibility", ROOT / "src/laishime/utils/mongo.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
update_document = MODULE.update_document


def ready(value):
    """ready returns an already completed future containing value."""
    result = Future()
    result.set_result(value)
    return result


class ModernCollection:
    """ModernCollection records single-document writes without a server."""
    def __init__(self, document=None):
        """__init__ initializes recorded writes and a find-one document."""
        self.calls = []
        self.document = document

    def update_one(self, selector, changes, upsert=False):
        """update_one records arguments and returns a completed driver-like result."""
        self.calls.append((selector, changes, upsert))
        return ready({"ok": 1})

    def find_one(self, *args, **kwargs):
        """find_one returns the fixture document."""
        return ready(self.document)

    def __getattr__(self, name):
        """__getattr__ models Motor's non-callable dynamic collection names."""
        return SimpleNamespace(name=name)


class LegacyCollection:
    """LegacyCollection exposes only the legacy update method."""
    def __init__(self):
        """__init__ initializes recorded write arguments."""
        self.calls = []

    def update(self, selector, changes, upsert=False):
        """update records legacy arguments and returns its unchanged result."""
        self.calls.append((selector, changes, upsert))
        return "legacy-result"

    def __getattr__(self, name):
        """__getattr__ models dynamic collection attributes on older drivers."""
        return SimpleNamespace(name=name)


class Cursor:
    """Cursor supplies deterministic documents to the actual statistics coroutine."""
    def __init__(self, documents):
        """__init__ stores documents without network access."""
        self.documents = iter(documents)
        self.current = None

    def max_time_ms(self, value):
        """max_time_ms preserves the fixture cursor's chainable API."""
        return self

    @property
    def fetch_next(self):
        """fetch_next advances once and returns whether a document is available."""
        self.current = next(self.documents, None)
        return ready(self.current is not None)

    def next_object(self):
        """next_object returns the current fixture document."""
        return self.current


def actual_method(name):
    """actual_method loads a real tweet coroutine without private startup imports."""
    revision = os.environ.get("LAISHIME_SOURCE_REV")
    source_file = os.environ.get("LAISHIME_SOURCE_FILE")
    source = Path(source_file).read_text() if source_file else subprocess.check_output(
        ["git", "show", revision + ":src/laishime/views/tweets.py"],
        cwd=ROOT, text=True) if revision else (
            ROOT / "src/laishime/views/tweets.py").read_text()
    tree = ast.parse(source)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
               and node.name == "TopicTweets")
    method = next(node for node in cls.body if isinstance(node, ast.FunctionDef)
                  and node.name == name)
    method.decorator_list = []
    namespace = {
        "log": logging.getLogger("test"), "datetime": datetime,
        "defaultdict": defaultdict, "update_document": update_document,
        "pymongo": pymongo, "traceback": __import__("traceback"), "ERROR": 1,
        "TWITTER_AUTH": {"CONSUMER_KEY": "fixture", "CONSUMER_SECRET": "fixture"},
        "OAuthHandler": lambda *args: SimpleNamespace(
            set_access_token=lambda *args: None),
        "API": lambda auth: SimpleNamespace(
            user_timeline=lambda **kwargs: [
                SimpleNamespace(_json={"id": 2}), SimpleNamespace(_json={"id": 1})]),
        "twitter_api_parser": lambda tweet: dict(tweet, topics=["offline"]),
    }
    module = ast.Module(body=[method], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), "actual-tweet-coroutine", "exec"),
         namespace)
    return gen.coroutine(namespace[name])


class MongoCompatibilityTests(unittest.TestCase):
    """MongoCompatibilityTests verifies writes without importing private configuration."""
    def test_legacy_dynamic_attributes_do_not_hide_update(self):
        """test_legacy_dynamic_attributes_do_not_hide_update preserves the old API."""
        collection = LegacyCollection()
        result = update_document(collection, {"id": 2}, {"$set": {"text": "hello"}},
                                 upsert=True)
        self.assertEqual(result, "legacy-result")
        self.assertEqual(collection.calls,
                         [({"id": 2}, {"$set": {"text": "hello"}}, True)])

    def test_modern_arguments_and_future_are_preserved(self):
        """test_modern_arguments_and_future_are_preserved checks single-document semantics."""
        collection = ModernCollection()
        result = update_document(collection, {"collection": "tweets"},
                                 {"$set": {"topics_count": {"offline": 2}}})
        self.assertEqual(result.result(), {"ok": 1})
        self.assertEqual(collection.calls[0][2], False)

    def test_actual_motor_pymongo_write_path_without_database(self):
        """test_actual_motor_pymongo_write_path_without_database exercises real driver dispatch."""
        loop = IOLoop()
        client = MotorClient("mongodb://127.0.0.1:1", connect=False, io_loop=loop)
        try:
            with patch.object(pymongo.collection.Collection, "_update_retryable",
                              return_value={"n": 1, "nModified": 1, "ok": 1,
                                            "updatedExisting": True}) as write:
                result = loop.run_sync(lambda: update_document(
                    client.twitter.tweets, {"id": 2}, {"$set": {"text": "hello"}},
                    upsert=True), timeout=5)
                self.assertEqual(result.modified_count, 1)
                self.assertEqual(write.call_args.args[:2],
                                 ({"id": 2}, {"$set": {"text": "hello"}}))
                self.assertTrue(write.call_args.args[2])
        finally:
            client.close()
            loop.close()

    def test_actual_statistics_method_preserves_selector_and_counts(self):
        """test_actual_statistics_method_preserves_selector_and_counts executes application code."""
        statistics = ModernCollection()
        tweets = SimpleNamespace(find=lambda query: Cursor([
            {"topics": ["offline", "ton"]}, {"topics": ["offline"]}]))
        messages = []
        finished = []
        handler = SimpleNamespace(db=SimpleNamespace(twitter=SimpleNamespace(
            tweets=tweets, statistics=statistics)), write_json=lambda **kw: messages.append(kw),
            finish=lambda: finished.append(True))
        loop = IOLoop()
        try:
            loop.run_sync(lambda: actual_method("update_statistics")(handler), timeout=5)
        finally:
            loop.close()
        selector, changes, upsert = statistics.calls[0]
        self.assertEqual(selector, {"collection": "tweets"})
        self.assertEqual(dict(changes["$set"]["topics_count"]), {"offline": 2, "ton": 1})
        self.assertFalse(upsert)
        self.assertEqual(messages, [{"msg": "updated ok"}])
        self.assertEqual(finished, [True])

    def test_actual_crawler_preserves_upsert_and_skips_old_tweets(self):
        """test_actual_crawler_preserves_upsert_and_skips_old_tweets uses only fixture API data."""
        tweets = ModernCollection({"id": 1})
        account = ModernCollection({"access_token": "fixture",
                                    "access_token_secret": "fixture"})
        messages = []
        finished = []
        handler = SimpleNamespace(db=SimpleNamespace(twitter=SimpleNamespace(
            tweets=tweets, account=account)), write_json=lambda **kw: messages.append(kw),
            finish=lambda: finished.append(True))
        loop = IOLoop()
        try:
            loop.run_sync(lambda: actual_method("crawler_tweets")(handler), timeout=5)
        finally:
            loop.close()
        self.assertEqual(tweets.calls,
                         [({"id": 2}, {"$set": {"id": 2, "topics": ["offline"]}}, True)])
        self.assertEqual(messages, [{"data": "success crawl 1 tweets"}])
        self.assertEqual(finished, [True])


if __name__ == "__main__":
    unittest.main()
