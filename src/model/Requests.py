import requests
from bs4 import BeautifulSoup
import time
import re
from threading import Thread
from model.Utils import stdout_log

url = "https://www.google.com/search?q={}&start={}&hl=en"  # hl = languages, cr = country


def geturls(keyword, pages):
    urls = []
    result_per_page = 10
    for x in range(0, pages):
        urls.append(url.format(keyword.replace(" ", "%20"), str(x * result_per_page)))
    return urls


def preprocess(response):
    if response.status_code == 200:
        try:
            soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        except UnicodeDecodeError:
            soup = BeautifulSoup(response.content, 'lxml')
        raw_doc = ' '.join(soup.find(id='desktop-search').find_all('tr')[0].strings)
        output = raw_doc
        output = re.compile('(\n|\t|\r|\xa0|\x08|\x03)').sub(' ', output)
        output = re.compile("\'").sub("'", output)
        output = re.compile(r"(.)([\u4e00-\u9fa5])").sub(r"\1 \2 ", output)  # add whitespace between chinese characters
        return output
    else:
        stdout_log("A thread reported status code == " + str(response.status_code))
        return None


def get_word_to_doc_threaded(keywords, mid, threads=20, wait_time=20, jail_time=7200):
    links = []
    for keyword in keywords:
        links.extend(geturls(keyword, 1))

    word_to_doc = {}
    length = len(links)
    i = 0
    t = [Thread() for _ in range(threads)]
    while i < length:
        fetched = False
        while not fetched:
            work_count = min(i + threads, length)
            stdout_log("#{}: Fetching data {}/{}...".format(mid, work_count, length))
            for j in range(work_count-i):
                t[j] = Thread(target=thread_worker, args=(links[i + j], keywords[i + j], word_to_doc))
                t[j].start()
            if work_count != length:
                time.sleep(wait_time)
            while True:
                if sum([x.is_alive() for x in t]) == 0:
                    break
                time.sleep(1)
            fetched = True
            for k, v in word_to_doc.items():
                if v is None:
                    fetched = False
                    break
            if not fetched:
                stdout_log("#{}: got blocked. lul. waiting {} mins...".format(mid, int(jail_time / 60)))
                time.sleep(jail_time)
        i += threads
    return word_to_doc


def thread_worker(link, keyword, word_to_doc):
    if not keyword in word_to_doc.keys() or word_to_doc[keyword] is None:
        session = requests.session()
        session.cookies.clear()
        response = session.get(link)
        word_to_doc[keyword] = preprocess(response)
