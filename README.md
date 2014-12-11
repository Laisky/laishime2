Laishime 2.1
---

python project for fun

[http://hime.laisky.us](http://hime.laisky.us)

### Deploy

#### Local

```sh
$ cd laishime2/1
$ python bootstrap.sh
$ bin/buildout install
$ bin/python setup.py develop
$ bin/python -m laishime
```

Supervisor 和 Nginx 的配置文件在 `laishime/1/deploy` 中

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
