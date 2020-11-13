from model.Requests import get_word_to_doc_threaded
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.cluster import KMeans
from model.Utils import create_json, stdout_log


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


def get_clusters(word_to_vec, k_range_min=20, k_range_max=30, max_iteration=300):
    X = np.zeros(shape=(len(word_to_vec), len(list(word_to_vec.items())[0][1])))
    for i, _ in enumerate(word_to_vec.values()):
        X[i, :] = _
    k = optimalK(X, nrefs=3, minClusters=k_range_min, maxClusters=k_range_max)
    estimator = KMeans(n_clusters=k, max_iter=max_iteration)
    y_pred = estimator.fit_predict(X)
    result = {}
    for x in range(k):
        result[str(x)] = []
    for i, _ in enumerate(word_to_vec.keys()):
        result[str(y_pred[i])].append(_)
    return result


def optimalK(data, nrefs=3, minClusters=1, maxClusters=15):
    stdout_log("Finding optimal k-count...")
    gaps = np.zeros((len(range(1, maxClusters)),))
    # resultsdf = pd.DataFrame({'clusterCount': [], 'gap': []})
    for gap_index, k in enumerate(range(minClusters, maxClusters)):

        # Holder for reference dispersion results
        refDisps = np.zeros(nrefs)

        # For n references, generate random sample and perform kmeans getting resulting dispersion of each loop
        for i in range(nrefs):
            # Create new random reference set
            randomReference = np.random.random_sample(size=data.shape)

            # Fit to it
            km = KMeans(k)
            km.fit(randomReference)

            refDisp = km.inertia_
            refDisps[i] = refDisp

        # Fit cluster to original data and create dispersion
        km = KMeans(k)
        km.fit(data)

        origDisp = km.inertia_

        # Calculate gap statistic
        gap = np.log(np.mean(refDisps)) - np.log(origDisp)

        # Assign this loop's gap statistic to gaps
        gaps[gap_index] = gap

        # resultsdf = resultsdf.append({'clusterCount': k, 'gap': gap}, ignore_index=True)

    # return (gaps.argmax() + 1, resultsdf)  # Plus 1 because index of 0 means 1 cluster is optimal, index 2 = 3 clusters are optimal
    k = gaps.argmax() + minClusters
    stdout_log("Optimal K is {}".format(k))
    return k

class ModelTrainer:
    def __init__(self, keywords, mid, model_only=False):
        self.mid = mid
        self.keywords = keywords
        if not model_only:
            create_json(self.mid)
        self.model_only = model_only
        self.result = None

    def __repr__(self):
        return "model.Trainer.ModelTrainer #" + self.mid

    def execute(self):
        word_to_doc = get_word_to_doc_threaded(self.keywords, self.mid)
        stdout_log("#{}: Training doc2vec model...".format(self.mid))
        if self.model_only:
            model = train(word_to_doc, vec_size=50, max_epochs=50)
            self.result = model
        else:
            model = train(word_to_doc)
            stdout_log("#{}: Creating clusters...".format(self.mid))
            word_to_vec = get_word_to_vec(model, word_to_doc)
            self.result = get_clusters(word_to_vec)
