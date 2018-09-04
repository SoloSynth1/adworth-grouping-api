from werkzeug.exceptions import NotFound, BadRequest

class ModelNotFound(NotFound):
    def __init__(self, mid):
        super(ModelNotFound, self).__init__()
        self.description = "Couldn't found a model with ID #{}.".format(mid)

class ModelInTraining(NotFound):
    def __init__(self, mid):
        super(ModelInTraining, self).__init__()
        self.description = "Result of model #{} is in training and is not yet available.".format(mid)

class MalformedRequestData(BadRequest):
    def __init__(self):
        super(MalformedRequestData, self).__init__()
        self.description = "Malformed Request. Please make sure parameter 'data' is a list of keywords in the JSON request."