import requests
from bs4 import BeautifulSoup
import re
from threading import Thread
import time
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.cluster import KMeans

url = "https://www.google.com/search?q={}&start={}&hl=en"  # hl = languages, cr = country

def geturls(keyword, pages):
    urls = []
    result_per_page = 10
    for x in range(0, pages):
        urls.append(url.format(keyword.replace(" ", "%20"), str(x * result_per_page)))
    return urls

def preprocess(soup):
    raw_doc = ' '.join(soup.find(id='desktop-search').find_all('tr')[0].strings)
    output = raw_doc
    output = re.compile('(\n|\t|\r|\xa0)').sub(' ', output)
    output = re.compile("\'").sub("'", output)
    output = re.compile(r"(.)([\u4e00-\u9fa5])").sub(r"\1 \2 ", output)  # add whitespace between chinese characters
    return output

def get_word_to_doc_threaded(keywords, threads=50):
    links = []
    for keyword in keywords:
        links.extend(geturls(keyword, 1))

    word_to_doc = {}
    l = len(links)
    i = 0
    while i < l:
        for j in range(threads):
            if i + j < l:
                t = Thread(target=thread_worker, args=(links[i + j], keywords[i + j], word_to_doc))
                t.start()
        print("{}/{}...".format(min(i + threads, l), l))
        i += threads
        t.join()
    return word_to_doc

def thread_worker(link, keyword, word_to_doc):
    soup = BeautifulSoup(requests.get(link).content, 'lxml')
    word_to_doc[keyword] = preprocess(soup)

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

class ModelTrainer():
    def __init__(self, keywords, id):
        self.id = str(id)
        self.keywords = keywords
        self.get_clusters()

    def get_clusters(self, vec_size=30):
        word_to_doc = get_word_to_doc_threaded(self.keywords, threads=50)
        while len(word_to_doc) != len(self.keywords):
            time.sleep(1)
        model = train(word_to_doc, self.id, vec_size)
        word_to_vec = get_word_to_vec(model, word_to_doc)
        result = get_clusters(word_to_vec)
        print(result)