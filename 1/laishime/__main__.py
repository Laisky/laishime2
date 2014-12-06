import wsgiref.simple_server

from laishime import application


server = wsgiref.simple_server.make_server('', 80, application)
server.serve_forever()
