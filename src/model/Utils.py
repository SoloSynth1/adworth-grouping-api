import os
import json
import datetime
import sys

def get_abspath():
    return os.path.dirname(os.path.abspath(__file__)) + '/clusters/'

def get_jsonpath(mid):
    return get_abspath() + '{}.json'.format(mid)

def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_json(mid):
    check_dir(get_abspath())
    with open(get_jsonpath(mid), 'w') as f:
        f.close()
    stdout_log(get_jsonpath(mid) + " created")

def dump_result(ModelTrainer):
    if ModelTrainer.model_only:
        filename = get_abspath() + '{}.d2vmodel'.format(ModelTrainer.mid)
        ModelTrainer.result.save(filename)
    elif not ModelTrainer.model_only:
        filename = get_jsonpath(ModelTrainer.mid)
        with open(filename, "w") as f:
            f.write(json.dumps(ModelTrainer.result))
            f.close()
    stdout_log(filename + " written")

def load_json(mid):
    try:
        with open(get_jsonpath(str(mid)), 'r') as f:
            clusters = json.loads(f.read())
            f.close()
        return clusters
    except Exception as e:
        raise e

def stdout_log(message):
    print("[{}] {}".format(datetime.datetime.now(),message), file=sys.stdout)