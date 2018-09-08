import os
import json

def get_abspath():
    return os.path.dirname(os.path.abspath(__file__)) + '/clusters/'

def get_jsonpath(mid):
    return get_abspath() + '{}.json'.format(mid)

def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_json(mid):
    check_dir(get_abspath())
    with open(get_jsonpath(mid), 'a') as f:
        f.close()
    print(get_jsonpath(mid) + " created")

def dump_pred(ModelTrainer):
    json_file = get_jsonpath(ModelTrainer.mid)
    with open(json_file, "w") as f:
        f.write(json.dumps(ModelTrainer.result))
        f.close()
    print(json_file + " written")

def load_json(mid):
    try:
        with open(get_jsonpath(str(mid)), 'r') as f:
            clusters = json.loads(f.read())
            f.close()
        return clusters
    except Exception as e:
        raise e
