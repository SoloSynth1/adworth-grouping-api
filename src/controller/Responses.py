from flask import jsonify


def response(message, payload=None):
    r = dict(payload or ())
    r['message'] = message
    return jsonify(r)
