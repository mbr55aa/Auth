# flask_app/pywsgi.py
from gevent import monkey
from gevent.pywsgi import WSGIServer

from app import app

monkey.patch_all()

http_server = WSGIServer(("", 5000), app)
http_server.serve_forever()
