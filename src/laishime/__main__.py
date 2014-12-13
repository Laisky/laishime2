import logging

import tornado.httpserver
import tornado.options as opt
from tornado.options import options

from . import Application


log = logging.getLogger(__name__)
opt.parse_config_file(options.config)
opt.parse_command_line()

http_server = tornado.httpserver.HTTPServer(Application())
http_server.listen(options.port)

if options.debug:
    log.info('start application in debug mode')
else:
    log.info('start application in normal mode')
tornado.ioloop.IOLoop.instance().start()
