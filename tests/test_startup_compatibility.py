"""Actual startup and HTTP dispatch tests with fixture configuration only."""
import ast
import io
import logging
from pathlib import Path
import re
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import tornado.gen
import tornado.testing
import tornado.web
import yaml

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = tempfile.TemporaryDirectory()
sys.path.insert(0, str(ROOT / "src"))
configuration = types.ModuleType("laishime.const")
configuration.CWD = str(ROOT / "src/laishime")
configuration.LOG_NAME = "laishime-offline-test"
configuration.LOG_LEVEL = logging.WARNING
configuration.LOG_PATH = str(Path(FIXTURE.name) / "test.log")
configuration.url_regex = re.compile(r"(https?://\S+)")
configuration.TWITTER_AUTH = {}
sys.modules["laishime.const"] = configuration
import laishime
from laishime.views.tweets import TopicTweets


class DelayedTweets(TopicTweets):
    """DelayedTweets exercises the actual get dispatcher with a delayed offline route."""
    @tornado.gen.coroutine
    def update_statistics(self):
        """update_statistics waits once and finishes with a deterministic JSON response."""
        yield tornado.gen.sleep(0.02)
        self.write_json(data="completed")
        self.finish()


class StartupCompatibilityTests(unittest.TestCase):
    """StartupCompatibilityTests verifies framework and packaging import boundaries."""
    def test_package_uses_a_supported_http_application(self):
        """test_package_uses_a_supported_http_application constructs the actual application."""
        with patch.object(laishime.Application, "setup_db"):
            application = laishime.Application()
        self.assertIsInstance(application, tornado.web.Application)
        self.assertIsNone(application.db if hasattr(application, "db") else None)

    def test_packaging_does_not_import_private_pip_apis(self):
        """test_packaging_does_not_import_private_pip_apis verifies original requirements."""
        with patch("setuptools.setup") as setup:
            runpy.run_path(str(ROOT / "setup.py"), run_name="metadata-control")
        values = setup.call_args.kwargs["install_requires"]
        self.assertIn("pymongo==4.6.3", values)
        self.assertIn("motor==3.5.3", values)

    def test_authorization_yaml_preserves_plain_data_and_rejects_python_tags(self):
        """test_authorization_yaml_preserves_plain_data_and_rejects_python_tags checks actual loader."""
        tree = ast.parse((ROOT / "src/laishime/const.py").read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name == "load_authorization")
        namespace = {"yaml": yaml}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                     "actual-authorization-loader", "exec"), namespace)
        with patch("builtins.open", return_value=io.StringIO("twitter_api:\n  mode: fixture\n")):
            self.assertEqual(namespace["load_authorization"]("fixture"),
                             {"twitter_api": {"mode": "fixture"}})
        with patch("builtins.open", return_value=io.StringIO("!!python/object/apply:builtins.str [fixture]")):
            with self.assertRaises(yaml.YAMLError):
                namespace["load_authorization"]("fixture")


class DispatchCompatibilityTests(tornado.testing.AsyncHTTPTestCase):
    """DispatchCompatibilityTests checks the real request dispatcher on local loopback."""
    def get_app(self):
        """get_app returns a fixture application using the actual inherited get method."""
        return tornado.web.Application([(r"/topic_tweets/(.*)", DelayedTweets)])

    def test_get_waits_for_coroutine_completion(self):
        """test_get_waits_for_coroutine_completion ensures the response is not finished early."""
        response = self.fetch("/topic_tweets/update-statistics")
        self.assertEqual(response.code, 200)
        self.assertIn(b'"data": "completed"', response.body)

    def test_unknown_route_preserves_404_redirect(self):
        """test_unknown_route_preserves_404_redirect retains the original redirect target."""
        response = self.fetch("/topic_tweets/unknown", follow_redirects=False)
        self.assertEqual(response.code, 302)
        self.assertEqual(response.headers["Location"], "/404.html")


def tearDownModule():
    """tearDownModule closes only the test-imported worker pool and fixture directory."""
    import laishime.utils
    laishime.utils._workers.close()
    laishime.utils._workers.join()
    FIXTURE.cleanup()


if __name__ == "__main__":
    unittest.main()
