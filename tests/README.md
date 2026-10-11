The offline MongoDB compatibility regressions exercise the two actual tweet
coroutines and the real Motor/PyMongo write dispatch. They also check legacy
update semantics and dynamically named collection attributes. No database or
Twitter request is sent, and private application configuration is not imported.

Qualified environment: Python 3.12.15, PyMongo 4.6.3, Motor 3.5.3 and Tornado
6.5.10. Run python -m unittest discover -s tests -v in that environment.
To reproduce the two old write failures, set LAISHIME_SOURCE_FILE to a copy of
the pre-repair src/laishime/views/tweets.py; use the same tests and dependencies.

The full application remains blocked on its historical runtime and startup
interfaces. README specifies Python 3.4.1, while PyMongo 4.6.3 requires >=3.7.
The resolved current Tornado lacks WSGIApplication and the asynchronous
decorator, and setup.py imports removed pip.req/pip.download internals. These
pre-existing startup/prerequisite failures must be resolved before merging or
claiming full-application acceptance. The focused adapter preserves the
single-document selector, update payload, upsert flag and yielded driver result.
