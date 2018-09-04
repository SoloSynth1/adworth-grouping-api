from flask import Flask
from controller.ExceptionHandler import JSONExceptionHandler
from controller.ModelController import modelController
from controller.Responses import response

port = 5000
app = Flask(__name__)
handler = JSONExceptionHandler(app)
app.register_blueprint(modelController)


@app.route("/status")
def status():
    return response("Status OK, ready to receive data.")


if __name__ == "__main__":
    app.run(port=port)
