from model.Utils import dump_pred
from model.Trainer import ModelTrainer
import time


class Queue():
    def __init__(self):
        self.list = []
        self.monitor()

    def __repr__(self):
        return self.list

    def insert(self, mt):
        if not isinstance(mt, ModelTrainer):
            print("invalid varible insertion to Queue")
            pass
        self.list.append(mt)

    def pop(self):
        self.list.pop(0)

    def monitor(self):
        while True:
            if len(self.list) > 0 and self.list[0].result is None:
                self.list[0].fit_predict()
                dump_pred(self.list[0])
                self.pop()
            time.sleep(60)
