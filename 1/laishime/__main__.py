import os

# import wsgiref.simple_server
import tornado.httpserver
import tornado.options as opt
from tornado.options import define, options

# from . import application
from . import Application
from .const import PWD


define("config", default=os.path.join(PWD, 'config', 'server.conf'))
define("port", default=27800, type=int)


opt.parse_config_file(options.config)
# server = wsgiref.simple_server.make_server('', options.port, application)
# server.serve_forever()
http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(options.port)
tornado.ioloop.IOLoop.instance().start()
