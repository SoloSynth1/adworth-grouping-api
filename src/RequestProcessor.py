from flask import request, Blueprint
from ExceptionHandler import ExceptionHandler

RequestProcessor = Blueprint('RequestProcessor', __name__)

@RequestProcessor.before_request
def only_json():
    print("triggered")
    print(request)
    if not request.is_json:
        raise ExceptionHandler('Malformed Request', status_code=400, payload=request.get_json())

@RequestProcessor.route('/lol')
def lol():
    return 'it works!!!'