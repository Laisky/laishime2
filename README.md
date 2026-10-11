Laishime 2.1
---

Originally a Python3.4 project for fun; the qualified dependency baseline is now Python3.10.

[http://hime.laisky.com](http://localhost:27800/topic_tweets/index.html)

### Deploy

#### Run

```sh
$ cd laishime2/src
$ python3 -m venv .
$ source bin/activate
$ bin/python setup.py develop
$ bin/python -m laishime [--debug=false] [--dbhost=127.0.0.1] [--dbport=27017]
```

Supervisor 和 Nginx 的配置文件在 `laishime/src/deploy` 中

### Backend

- Python>=3.10
    - tornado
    - jinja2
    - motor
- Nginx
- Supervisor

### Frontend

- HTML5 & CSS & JavaScript
- Bootstrap_v2
- jQuery_v1.11

## Dependency compatibility acceptance

The PyMongo4.18.3 upgrade requires a newer interpreter than the original Python3.4
experiment. Current acceptance covers Python3.10.22 and Python3.12.15 with
Motor3.7.1 and Tornado6.5.10. Packaging rejects unsupported older interpreters.
The compatibility adapter preserves legacy single-document writes and the HTTP
entry point awaits asynchronous handlers before finishing responses. Existing
configuration values and deployment files are unchanged.

Run python -m unittest discover -s tests -v after installing requirements.txt
and setuptools. The suite uses fixture configuration, a local HTTP server and
mocked database writes; it sends no Twitter/MongoDB request or deployment.
