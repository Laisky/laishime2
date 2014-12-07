import os

import wsgiref.simple_server
import tornado.options as opt
from tornado.options import define, options

from laishime import application
from laishime.const import PWD


define("config", default=os.path.join(PWD, 'config', 'server.conf'))
define("port", default=8080, type=int)


opt.parse_config_file(options.config)
server = wsgiref.simple_server.make_server('', options.port, application)
server.serve_forever()
