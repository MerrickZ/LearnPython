#!/usr/bin/python3
import configparser
import os
import re
import shutil
import sys
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
    "verifyCert": "yes"
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
        requests.packages.urllib3.disable_warnings()
    except:
        pass


def download(url):
    if not (config['host'] in url):
        return
    uri = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(uri.query)

    tid = params['tid']
    if not tid:
        return

    src = fetch(url)
    title = extract_title(src, full=True)
    print('+%s' % title)

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
                hive.append(_url)

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
                hive.append(_u)
            else:
                hive.append(config['host'] + _u)
    except ValueError:
        pass

    # SKIP DOWNLOADED FILES
    if (os.path.exists("%s-%s.html" % (tid, title))):
        print("#%s-%s.html already exists." % (tid, title), file=sys.stderr)
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
            print("Error writing %s" % title, file=sys.stderr)


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

    # Init Hive
    hive = [url]
    downloaded = set()

    while hive:
        current_url = hive.pop()
        if (current_url in downloaded):
            pass
        else:
            print(r"~[%2d]%s" % (len(hive), current_url))
            download(current_url)
            downloaded.add(current_url)
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
