from controller.Errors import MalformedRequestData, ModelNotFound, ModelInTraining
from flask import Blueprint, request
from controller.Responses import response
from model.Trainer import ModelTrainer
import time
from threading import Thread
import json
import os

modelController = Blueprint("modelController", __name__)


@modelController.route("/model/<int:mid>", methods=['GET'])
def report_model_status(mid):
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(parent_dir+'/model/model_list.csv', 'r') as f:
            model_list = [int(x) for x in f.readlines()]
            f.close()
        if mid in model_list:
            try:
                with open(parent_dir+'/../model/clusters/{}.json'.format(str(mid)), 'r') as f:
                    clusters = json.loads(f.read())
                    f.close()
                payload = {'clusters': clusters,
                           'id': mid}
                return response("Retrieve Sucessful", payload=payload)
            except FileNotFoundError:
                raise ModelInTraining(mid)
        else:
            raise ModelNotFound(mid)
    except FileNotFoundError:
        raise ModelNotFound(mid)


@modelController.route("/model/create", methods=['POST'])
def create_model():
    request_dict = request.json
    if 'data' in request_dict.keys() and isinstance(request_dict['data'], list):
        mid = int(time.time())
        t = Thread(target=ModelTrainer, args=(uniquify(request_dict['data']), str(mid)))
        t.start()
        payload = {'id': mid}
        return response("Model Request Created Successfully", payload)
    else:
        raise MalformedRequestData()


def uniquify(input_list):
    try:
        return list(set([str(x) for x in input_list]))
    except:
        raise MalformedRequestData()
