from model.Requests import get_word_to_doc_threaded
import time
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.cluster import KMeans
import json
import os

def train(word_to_doc, model_id, vec_size=30, max_epochs=100, alpha=0.025):
    tagged_data = [TaggedDocument(words=word_tokenize(value.lower()), tags=[key]) for key, value in word_to_doc.items()]

    model = Doc2Vec(vector_size=vec_size,
                    alpha=alpha,
                    min_alpha=0.00025,
                    min_count=1,
                    dm=1)

    model.build_vocab(tagged_data)

    for epoch in range(max_epochs):
        # print('Epoch {0}/{1}...'.format(epoch, max_epochs))
        model.train(tagged_data,
                    total_examples=model.corpus_count,
                    epochs=model.epochs)
        # decrease the learning rate
        model.alpha -= 0.0002
        # fix the learning rate, no decay
        model.min_alpha = model.alpha

    # model.save("data/"+ model_id + "_d2v.model")
    # print("Model Saved")
    return model


def get_word_to_vec(model, word_to_doc):
    word_to_vec = {}
    for key in word_to_doc.keys():
        word_to_vec[key] = model.docvecs[key]
    return word_to_vec


def get_clusters(word_to_vec, k=5, max_iteration=300):
    X = np.zeros(shape=(len(word_to_vec), len(list(word_to_vec.items())[0][1])))
    for i, _ in enumerate(word_to_vec.values()):
        X[i, :] = _
    estimator = KMeans(n_clusters=k, max_iter=max_iteration)
    y_pred = estimator.fit_predict(X)
    result = {}
    for x in range(k):
        result[str(x)] = []
    for i, _ in enumerate(word_to_vec.keys()):
        result[str(y_pred[i])].append(_)
    return result


def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


class ModelTrainer:
    def __init__(self, keywords, mid):
        self.abspath = os.path.dirname(os.path.abspath(__file__))
        self.mid = str(mid)
        self.json_path = self.abspath+ '/clusters/{}.json'.format(self.mid)
        self.keywords = keywords
        self.record_id()
        self.get_clusters()

    def get_clusters(self, vec_size=30):
        word_to_doc = get_word_to_doc_threaded(self.keywords, threads=100)
        while len(word_to_doc) != len(self.keywords):
            time.sleep(1)
        model = train(word_to_doc, self.mid, vec_size)
        word_to_vec = get_word_to_vec(model, word_to_doc)
        result = get_clusters(word_to_vec)
        check_dir(self.abspath+'/clusters/')
        with open(self.json_path, "w") as f:
            f.write(json.dumps(result))
            f.close()
        print(self.json_path + " written")

    def record_id(self):
        with open(self.json_path, 'a') as f:
            f.close()
