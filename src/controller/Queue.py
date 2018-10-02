from model.Utils import dump_pred
from model.Trainer import ModelTrainer
import time

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        else:
            cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Queue(metaclass=Singleton):

    def __init__(self):
        if not hasattr(self,'list'):
            self.list = []

    def insert(self, mt):
        if isinstance(mt, ModelTrainer):
            self.list.append(mt)
        else:
            print("invalid varible insertion to Queue, breaking...")


    def pop(self):
        self.list.pop(0)

    def monitor(self):
        while True:
            if len(self.list) > 0 and self.list[0].result is None:
                self.list[0].fit_predict()
                dump_pred(self.list[0])
                self.pop()
            time.sleep(5)
