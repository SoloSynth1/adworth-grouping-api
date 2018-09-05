import requests
from bs4 import BeautifulSoup
import re
from threading import Thread
import time
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from nltk.tokenize import word_tokenize
import numpy as np
from sklearn.cluster import KMeans
import json
import os

url = "https://www.google.com/search?q={}&start={}&hl=en"  # hl = languages, cr = country


def geturls(keyword, pages):
    urls = []
    result_per_page = 10
    for x in range(0, pages):
        urls.append(url.format(keyword.replace(" ", "%20"), str(x * result_per_page)))
    return urls


def preprocess(soup):
    try:
        raw_doc = ' '.join(soup.find(id='desktop-search').find_all('tr')[0].strings)
        output = raw_doc
        output = re.compile('(\n|\t|\r|\xa0)').sub(' ', output)
        output = re.compile("\'").sub("'", output)
        output = re.compile(r"(.)([\u4e00-\u9fa5])").sub(r"\1 \2 ", output)  # add whitespace between chinese characters
        return output
    except:
        return None


def get_word_to_doc_threaded(keywords, threads=20):
    links = []
    for keyword in keywords:
        links.extend(geturls(keyword, 1))

    word_to_doc = {}
    length = len(links)
    i = 0
    t = [None for _ in range(threads)]
    while i < length:
        fetched = False
        while not fetched:
            try:
                work_count = min(i + threads, length)
                print("{}/{}...".format(work_count, length))
                for j in range(threads):
                    if i + j < length:
                        t[j] = Thread(target=thread_worker, args=(links[i + j], keywords[i + j], word_to_doc))
                        t[j].start()
                while len(word_to_doc) != work_count:
                    time.sleep(1)
                for k, v in word_to_doc.items():
                    if v == None:
                        raise e
                fetched = True
            except Exception as e:
                # wait for google search to unblock
                fetched = False
                print("got blocked. lul\nwaiting 60 mins...")
                time.sleep(3600)
                continue
        for thread in t:
            thread.join()
        i += threads
    return word_to_doc


def thread_worker(link, keyword, word_to_doc):
    if not keyword in word_to_doc.keys() or word_to_doc[keyword] != None:
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
        with open(self.abspath+'/model_list.csv', 'a') as f:
            f.writelines(self.mid+'\n')
            f.close()
