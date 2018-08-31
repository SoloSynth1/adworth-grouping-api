from flask import Flask, request, jsonify, abort
from ExceptionHandler import ExceptionHandler
from RequestProcessor import RequestProcessor
from Response import response

app = Flask(__name__)
app.register_blueprint(RequestProcessor)

@app.errorhandler(ExceptionHandler)
def handle_exception(error):
    response = error.to_dict()
    response.status_code = error.status_code
    return response

@app.errorhandler(Exception)
def handle_exception(error):
    response = error.to_dict()
    response.status_code = error.status_code
    return response


@app.route("/error", methods=['GET', 'POST'])
def error():
    abort(404)

@app.route("/compute", methods=['POST'])
def compute():
    json = request.get_json()
    check = 'data' in json.keys()
    return str(check)

@app.route("/status")
def status():
    return response("Status is OK, ready to receive data.", 200)

if __name__ == "__main__":
    app.run(port=5000)