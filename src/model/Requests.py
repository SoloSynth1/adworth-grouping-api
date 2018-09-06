from random import choice
import requests
from bs4 import BeautifulSoup
import time
import re
from threading import Thread

desktop_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.99 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.71 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.98 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.98 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.71 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.99 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/62.0']

url = "https://www.google.com/search?q={}&start={}&hl=en"  # hl = languages, cr = country


def geturls(keyword, pages):
    urls = []
    result_per_page = 10
    for x in range(0, pages):
        urls.append(url.format(keyword.replace(" ", "%20"), str(x * result_per_page)))
    return urls


def preprocess(response):
    if response.status_code == 200:
        soup = BeautifulSoup(response.content.decode('utf-8'), 'lxml')
        raw_doc = ' '.join(soup.find(id='desktop-search').find_all('tr')[0].strings)
        output = raw_doc
        output = re.compile('(\n|\t|\r|\xa0)').sub(' ', output)
        output = re.compile("\'").sub("'", output)
        output = re.compile(r"(.)([\u4e00-\u9fa5])").sub(r"\1 \2 ", output)  # add whitespace between chinese characters
        return output
    else:
        print("A thread reported status code != 200")
        return None


def get_word_to_doc_threaded(keywords, threads=20, wait_time=1800):
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
            work_count = min(i + threads, length)
            print("{}/{}...".format(work_count, length))
            for j in range(threads):
                if i + j < length:
                    t[j] = Thread(target=thread_worker, args=(links[i + j], keywords[i + j], word_to_doc))
                    t[j].start()
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
                print("got blocked. lul\nwaiting {} mins...".format(int(wait_time/60)))
                time.sleep(wait_time)
        # for thread in t:
        #     thread.join()
        i += threads
    return word_to_doc


def thread_worker(link, keyword, word_to_doc):
    if not keyword in word_to_doc.keys() or word_to_doc[keyword] is None:
        response = requests.get(link)
        word_to_doc[keyword] = preprocess(response)


def random_headers():
    return {
            'User-Agent': choice(desktop_agents),
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
