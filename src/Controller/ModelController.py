from Controller.Errors import MalformedRequestData, ModelNotFound
from flask import Blueprint, jsonify, request
from Controller.Responses import response
import time

modelController = Blueprint("modelController", __name__)

@modelController.route("/model/<int:mid>/status", methods=['GET'])
def report_model_status(mid):
    if mid != 0:
        raise ModelNotFound(mid)
    else:
        # TODO
        return jsonify({'status': "OK", "id": 0})

# @modelController.route("/model/<int:mid>/result", methods=['GET'])
# def report_clustering(mid):
#     if mid != 0:
#         raise ModelNotFound(mid)
#     else:
#         # TODO
#         return jsonify({'status': "OK", "id": 0})

@modelController.route("/model/create", methods=['POST'])
def create_model():
    request_dict = request.json
    if 'data' in request_dict.keys() and type(request_dict['data']) == type([]):
        id = int(time.time())
        # TODO: pass ID to train a model
        payload = {}
        payload['id'] = id
        return response("Model Request Created Successfully", payload)
    else:
        raise MalformedRequestData()

