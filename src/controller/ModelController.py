from controller.Errors import MalformedRequestData, ModelNotFound, ModelInTraining, TooFewKeywords
from flask import Blueprint, request
from controller.Responses import response
from model.Trainer import ModelTrainer
from controller.Queue import Queue
import time
from model.Utils import load_json
import hashlib
import sys

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
    print('ModelController received request: {}'.format(request.json), file=sys.stdout)
    if request_dict is not None and 'data' in request_dict.keys() and isinstance(request_dict['data'], list):
        unique_words = uniquify(request_dict['data'])
        if len(unique_words) >= 5:
            q = Queue()
            mid = hashlib.sha1(str(time.time()).encode('utf-8')).hexdigest()
            q.insert(ModelTrainer(unique_words, mid))
            payload = {'id': mid,
                       'training_queue': q.get_current_queue()}
            return response("Model Request Created Successfully", payload)
        else:
            raise TooFewKeywords()
    else:
        raise MalformedRequestData()


def uniquify(input_list):
    try:
        return list(set([str(x) for x in input_list if str(x) != '' and not x is None]))
    except:
        raise MalformedRequestData()
