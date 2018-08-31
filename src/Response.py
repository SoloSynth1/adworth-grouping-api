from flask import jsonify

def response(message, status_code=200, payload=None):
    r = dict(payload or ())
    r['message'] = message
    r['status_code'] = status_code
    return jsonify(r)