Laishime 2.1
---

Python3.4 project for fun

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

- Python==3.4.1
    - tornado
    - jinja2
    - motor
- Nginx
- Supervisor

### Frontend

- HTML5 & CSS & JavaScript
- Bootstrap_v2
- jQuery_v1.11
