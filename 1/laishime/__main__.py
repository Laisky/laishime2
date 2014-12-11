# import wsgiref.simple_server
import tornado.httpserver
import tornado.options as opt
from tornado.options import options

# from . import application
from . import Application


opt.parse_config_file(options.config)
opt.parse_command_line()
# server = wsgiref.simple_server.make_server('', options.port, application)
# server.serve_forever()
http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(options.port)
tornado.ioloop.IOLoop.instance().start()
