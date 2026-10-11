The offline MongoDB compatibility regressions exercise the two actual tweet
coroutines and the real Motor/PyMongo write dispatch. They also check legacy
update semantics and dynamically named collection attributes. No database or
Twitter request is sent, and private application configuration is not imported.

Qualified environment: Python 3.12.15, PyMongo 4.6.3, Motor 3.5.3 and Tornado
6.5.10. Run python -m unittest discover -s tests -v in that environment.
To reproduce the two old write failures, set LAISHIME_SOURCE_FILE to a copy of
the pre-repair src/laishime/views/tweets.py; use the same tests and dependencies.

Additional regressions import the actual application with fixture configuration,
construct its HTTP application, exercise delayed request dispatch and 404
redirects, validate safe authorization YAML and inspect packaging metadata.
The secure dependency baseline requires Python>=3.10 and is tested on 3.10.22
and 3.12.15. The historical Python3.4 runtime is not claimed supported.
Private configuration, real MongoDB/Twitter integration, notebooks and
deployment are outside this offline acceptance.
