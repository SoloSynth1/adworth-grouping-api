from flask import Flask
from Controller.ExceptionHandler import JSONExceptionHandler
from Controller.ModelController import modelController
from Controller.Responses import response

app = Flask(__name__)
handler = JSONExceptionHandler(app)
app.register_blueprint(modelController)

@app.route("/status")
def status():
    return response("Status OK, ready to receive data.")

if __name__ == "__main__":
    app.run(port=5000)