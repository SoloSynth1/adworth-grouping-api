from flask import Flask
from controller.ExceptionHandler import JSONExceptionHandler
from controller.ModelController import modelController
from controller.Responses import response
from controller.Queue import Queue
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
import werkzeug.serving
import argparse
from threading import Thread

app = Flask(__name__)
handler = JSONExceptionHandler(app)
app.register_blueprint(modelController)


@app.route("/status")
def status():
    q = Queue()
    payload = {'training_queue' : str(q.list)}
    return response("Status OK, ready to receive data.", payload)

def run_twisted_wsgi(port=8000):
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(port, site)
    reactor.run(**reactor_args)

def parse_arguments():
    parser = argparse.ArgumentParser(description='GroupAPI')
    parser.add_argument('-p', '--port', help='Port to listen on', required=False)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    # app.run()     # DO NOT USE FOR PRODUCTION
    reactor_args = {}
    if app.debug:
        reactor_args['installSignalHandlers'] = 0       # Disable twisted signal handlers in development only.
        run_twisted_wsgi = werkzeug.serving.run_with_reloader(run_twisted_wsgi)     # Turn on auto reload.
    args = parse_arguments()

    q = Queue()
    t = Thread(target=q.monitor)
    t.start()

    if not args.port is None and not isinstance(args.port, list) and args.port.isdigit():
        run_twisted_wsgi(int(args.port))
    else:
        run_twisted_wsgi()
