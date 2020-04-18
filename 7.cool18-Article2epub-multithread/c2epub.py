#!/usr/bin/python3
import configparser
import os
import queue
import re
import shutil
import sys
import threading
import time
import urllib

import bs4
import chardet
import html2epub
import requests

# requires: requests bs4 lxml pysocks html2epub

config = {
    "enableProxy": "no",
    "proxy": "socks5://127.0.0.1:1081",
    "minContent": 1000,
    "waitPackage": "no",
    "autoDelete": "yes",
    "verifyCert": "yes",
    "threads": 3
}


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


def to_str(bytes_or_str):
    codec = chardet.detect(bytes_or_str)
    value = bytes_or_str.decode(encoding=codec['encoding'])
    return value


def fetch(url):

    if config['enableProxy'] == 'yes':
        proxy = config['proxy']
        proxies = dict(http=proxy, https=proxy)
        try:
            resp = requests.get(url, proxies=proxies, verify=(
                config['verifyCert'] == 'yes'))
            src = to_str(resp.content)
            return src
        finally:
            pass
    else:
        try:
            resp = requests.get(url)
            src = to_str(resp.content)
            return src
        except:
            return ""


P_START = "<!--bodybegin-->"
P_END = "<!--bodyend-->"
L_START = '''<a name="followups" style=''>'''
L_END = '''<a name="postfp">'''


def clean_title(_title):
    title = _title.replace(" - cool18.com", "")
    title = title.replace("/", "-")
    title = title.replace("\\", "-")
    title = title.replace("*", "-")
    title = title.replace("?", "-")
    title = title.replace("<", "-")
    title = title.replace(">", "-")
    title = title.replace("|", "-")
    title = title.replace(":", "-").strip()
    return title


def extract_title(content, full=False):
    title_left = content.find('<title>')+len('<title>')
    title_right = content.find('</title>')
    title = content[title_left:title_right]

    if (full):
        title = clean_title(title)
    else:
        title_search = re.search('[《](.*?)[》]', title, re.IGNORECASE)
        if title_search:
            title = title_search.group(1)
        else:
            title_search = re.search('[【](.*?)[】]', title, re.IGNORECASE)
            if title_search:
                title = title_search.group(1)
            else:
                title = clean_title(title)
    return title


def should_ignore_this_link(_title):
    iwords = ["银元奖励", "无内容", "版块基金", " 给 ", "幸运红包"]
    for i in iwords:
        if i in _title:
            return True
    return False


def loadConfig():
    cf = configparser.ConfigParser()
    try:
        cf.read('config.ini')
        config['enableProxy'] = cf.get('network', 'enableProxy')
        config['proxy'] = cf.get('network', 'proxy')
        config['minContent'] = cf.get('config', 'minContent')
        config['waitPackage'] = cf.get('config', 'waitPackage')
        config['verifyCert'] = cf.get('network', 'verifyCert')
        config['threads'] = cf.get('config', 'threads')
        requests.packages.urllib3.disable_warnings()
    except:
        pass


def download(url,threadname):

    uri = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(uri.query)

    tid = params['tid']
    if not tid:
        return

    src = fetch(url)
    title = extract_title(src, full=True)
    print(f'{threadname}:GOT {title}')
    # REMOVE BLANKS
    raw = str(src)

    try:
        pos_start = raw.find(P_START)+len(P_START)
        pos_end = raw.find(P_END)
        page_content = raw[pos_start:pos_end]
        content_soup = bs4.BeautifulSoup(page_content, "lxml")
        # extract in page chapters
        links = content_soup.find_all('a')
        for a in links:
            _title = a.getText()
            #print('+%s' % _title)
            _url = a.get('href')
            if (_url and len(_url.strip()) > 8):
                if config['host'] in _url and not (_url in downloaded):
                    workqueue.put(_url)
            a.extract()
    except ValueError:
        return

    try:
        # extract below links
        lpos_start = raw.find(L_START)+len(L_START)
        lpos_end = raw.find(L_END)
        comments = raw[lpos_start:lpos_end]
        comm_soup = bs4.BeautifulSoup(comments, "lxml")
        for a in comm_soup.find_all('a'):
            _title = a.getText()
            if should_ignore_this_link(_title):
                continue
            #print('+%s' % _title)
            _u = a.get('href')
            if (_u and _u.startswith("http")):
                if config['host'] in _u and not (_u in downloaded):
                    workqueue.put(_u)
            else:
                _u = config['host'] + _u
                if config['host'] in _u and not (_u in downloaded):
                    workqueue.put(_u)
    except ValueError:
        pass
    downloading.pop()
    # SKIP DOWNLOADED FILES
    if (os.path.exists("%s-%s.html" % (tid, title))):
        print(f"{threadname}:SKP {tid}-{title}.html" , file=sys.stderr)
        return

    [s.extract() for s in content_soup('script')]
    # Wash Text
    page_content = str(content_soup.find('body').getText())
    page_content = page_content.replace(" ", "")
    page_content = page_content.replace("　　", "@@@@@@@@")
    page_content = page_content.replace(os.linesep, "@@@@@@@@")
    page_content = page_content.replace("\n", "@@@@@@@@")
    page_content = page_content.replace('cool18.com', '@@@@@@@@')
    page_content = page_content.replace('www.6park.com', '')
    page_content = page_content.replace('6park.com', '')
    page_content = page_content.replace("@@@@@@@@@@@@@@@@", "</p><p>")
    page_content = page_content.replace("@@@@@@@@", "</p><p>")
    page_content = page_content.replace("</p><p></p><p>", "</p><p>")

    try:
        last_pos = page_content.rindex('评分完成')
        page_content = page_content[:last_pos]
    except ValueError:
        pass

    if (len(page_content.strip()) > int(config['minContent'])):
        try:
            with open("%s-%s.html" % (tid, title), 'w+', encoding='utf-8', errors='ignore') as file:
                file.write("""<?xml version="1.0" encoding="utf-8" standalone="no"?>
                <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
                <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN">
                <head>
                <title>""")
                file.write(title)
                file.write(r"</title></head><body><p>")
                file.write(page_content)
                file.write(r"</p></body></html>")
        except:
            print(f"{threadname}:Error writing {title}", file=sys.stderr)
    else:
        print(f'{threadname}:IGN {title}')
    # add to downloaded
    downloaded.add(url)


class fetcher(threading.Thread):
    def __init__(self, name, q):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.daemon=True

    def run(self):
        while not exitflag:
            url = None
            threadlock.acquire()
            if (not workqueue.empty()):
                url = workqueue.get()
            threadlock.release()
            if (url):
                downloading.append(url)
                download(url,self.name)


workqueue = queue.Queue()
threads = []
downloaded = set()
threadlock = threading.Lock()
exitflag = 0
downloading = []

# Main Logic
if __name__ == '__main__':
    args_length = len(sys.argv)
    url = None
    if (args_length > 1):
        url = sys.argv[1]
    if (not url):
        url = str(input("请粘贴cool18站的文章网址:"))
    loadConfig()
    pypath = sys.argv[0]
    pydir = os.getcwd()

    config['host'] = url[:url.rindex('/')+1]

    src = fetch(url)
    title = extract_title(src)

    if not os.path.exists(title):
        os.mkdir(title)
    os.chdir(title)
    exitflag = 0

    tid = 0
    # Init Q
    workqueue.put(url)

    t = fetcher(f"T{tid}", workqueue)
    tid += 1
    threads.append(t)
    t.start()

    while downloading or not workqueue.empty():
        time.sleep(0.1)
        if len(threads) < int(config['threads']):
            t = fetcher(f"T{tid}", workqueue)
            tid += 1
            threads.append(t)
            t.start()
        pass

    # Queue is empty, exit.
    exitflag = 1

    print(">Download completed.")
    if config['waitPackage'] == 'yes':
        input('>Press Enter to pack files into epub...')

    print(">now packaging epub...")
    epub = html2epub.Epub(title, language="zh-cn",
                          creator="cool18", publisher="cool18")
    for file in os.listdir("."):
        chap = html2epub.create_chapter_from_file(file)
        epub.add_chapter(chap)
    epubpath = epub.create_epub(pydir)
    print(">OK, epub generated at: %s" % epubpath)

    if config['autoDelete'] == 'yes':
        os.chdir("..")
        print(">Deleting Directory: %s" % title)
        shutil.rmtree(title)
