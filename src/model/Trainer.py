from model.Requests import get_word_to_doc_threaded
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.cluster import KMeans
from model.Utils import create_json, dump_pred


def train(word_to_doc, vec_size=32, max_epochs=150, alpha=0.025):
    tagged_data = [TaggedDocument(words=word_tokenize(value.lower()), tags=[key]) for key, value in word_to_doc.items()]

    model = Doc2Vec(vector_size=vec_size, alpha=alpha, min_alpha=0.00025, min_count=1, dm=1)
    model.build_vocab(tagged_data)

    for epoch in range(max_epochs):
        model.train(tagged_data,
                    total_examples=model.corpus_count,
                    epochs=model.epochs)
        model.alpha -= 0.0002
        model.min_alpha = model.alpha
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


class ModelTrainer:
    def __init__(self, keywords, mid):
        self.mid = mid
        create_json(self.mid)
        self.keywords = keywords
        self.result = None
        # self.result = self.fit_predict()
        # dump_pred(self.mid, self.result)

    def __repr__(self):
        return "model.Trainer.ModelTrainer #" + self.mid

    def fit_predict(self):
        word_to_doc = get_word_to_doc_threaded(self.keywords, self.mid)
        print("#{}: Training doc2vec model...".format(self.mid))
        model = train(word_to_doc)
        word_to_vec = get_word_to_vec(model, word_to_doc)
        self.result = get_clusters(word_to_vec)
