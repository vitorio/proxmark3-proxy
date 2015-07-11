__author__ = 'vitorio'

from gevent.wsgi import WSGIServer
from pm3expect import app

http_server = WSGIServer(('', 5000), app)
http_server.serve_forever()