from controller.Errors import MalformedRequestData, ModelNotFound, ModelInTraining
from flask import Blueprint, request
from controller.Responses import response
from model.Trainer import ModelTrainer
from controller.Queue import Queue
import time
from model.Utils import load_json
import hashlib

modelController = Blueprint("modelController", __name__)


@modelController.route("/model/<mid>", methods=['GET'])
def report_model_status(mid):
    try:
        clusters = load_json(mid)
        payload = {'clusters': clusters,
                   'id': mid}
        return response("Retrieve Sucessful", payload=payload)
    except FileNotFoundError:
        raise ModelNotFound(mid)
    except Exception:
        raise ModelInTraining(mid)


@modelController.route("/model/create", methods=['POST'])
def create_model():
    request_dict = request.json
    if 'data' in request_dict.keys() and isinstance(request_dict['data'], list):
        q = Queue()
        mid = hashlib.sha1(str(time.time()).encode('utf-8')).hexdigest()
        q.insert(ModelTrainer(uniquify(request_dict['data']), mid))
        payload = {'id': mid,
                   'training_queue': str(q.list)}
        return response("Model Request Created Successfully", payload)
    else:
        raise MalformedRequestData()


def uniquify(input_list):
    try:
        return list(set([str(x) for x in input_list]))
    except:
        raise MalformedRequestData()
