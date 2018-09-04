from flask import Flask
from controller.ExceptionHandler import JSONExceptionHandler
from controller.ModelController import modelController
from controller.Responses import response
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
import werkzeug.serving

app = Flask(__name__)
handler = JSONExceptionHandler(app)
app.register_blueprint(modelController)


@app.route("/status")
def status():
    return response("Status OK, ready to receive data.")

def run_twisted_wsgi():
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(5000, site)
    reactor.run(**reactor_args)

if __name__ == "__main__":
    # app.run()     # DO NOT USE FOR PRODUCTION
    reactor_args = {}
    if app.debug:
        reactor_args['installSignalHandlers'] = 0       # Disable twisted signal handlers in development only.
        run_twisted_wsgi = werkzeug.serving.run_with_reloader(run_twisted_wsgi)     # Turn on auto reload.
        
    run_twisted_wsgi()