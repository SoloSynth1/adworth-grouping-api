from controller.Errors import MalformedRequestData, ModelNotFound
from flask import Blueprint, jsonify, request
from controller.Responses import response
from model.train import ModelTrainer
import time

modelController = Blueprint("modelController", __name__)

@modelController.route("/model/<int:mid>", methods=['GET'])
def report_model_status(mid):
    if mid != 0:
        raise ModelNotFound(mid)
    else:
        # TODO
        return jsonify({'status': "OK", "id": mid})

@modelController.route("/model/create", methods=['POST'])
def create_model():
    request_dict = request.json
    if 'data' in request_dict.keys() and type(request_dict['data']) == type([]):
        id = int(time.time())
        mt = ModelTrainer(request_dict['data'], str(id))
        payload = {}
        payload['id'] = id
        return response("Model Request Created Successfully", payload)
    else:
        raise MalformedRequestData()

