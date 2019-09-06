#!/usr/bin/python3
import configparser
import os
import re
import sys

import bs4
import requests

import html2epub

# requires: requests bs4 lxml pysocks html2epub

config = {
    "enableProxy": "yes",
    "proxy": "socks5://127.0.0.1:1081",
    "minContent": 1000,
    "waitPackage": "no"
}


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value


def fetch(url):
    # Change to your own proxy.
    if config['enableProxy'] == 'yes':
        proxy = config['proxy']
        proxies = dict(http=proxy, https=proxy)
        try:
            resp = requests.get(url, proxies=proxies)
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


def download(url):
    if (url.find("cool18.com") < 0):
        return

    # GET TID

    tid = ""
    tid_search = re.search('tid=(\d+)', url, re.IGNORECASE)
    if tid_search:
        tid = tid_search.group(1)
    else:
        return

    P_START = "<!--bodybegin-->"
    P_END = "<!--bodyend-->"
    L_START = '''<a name="followups" style=''>'''
    L_END = '''<a name="postfp">'''

    src = fetch(url)

    # GET TITLE
    title_search = re.search(r'<title>(.+)</title>', src, re.IGNORECASE)
    title = ""
    if title_search:
        title = title_search.group(1).replace(" - cool18.com", "").strip()
    else:
        title = "Unknown"
    print('>>> %s' % title)

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
            print(_title)

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
            if (_title.find('银元奖励') > -1) or (_title.find('无内容') > -1) or (_title.find('版块基金') > -1):
                continue
            print(_title)
            _u = a.get('href')
            if (_u and _u.startswith("http")):
                hive.append(_u)
            else:
                hive.append('https://www.cool18.com/bbs4/%s' % _u)
    except ValueError:
        pass
    [s.extract() for s in content_soup('script')]

    page_content = str(content_soup.find('body').getText())
    page_content = page_content.replace(
        'cool18.com', '\n').replace('www.6park.com', '').replace('6park.com', '').replace("\n", "</p><p>")
    try:
        last_pos = page_content.rindex('评分完成')
        page_content = page_content[:last_pos]
    except ValueError:
        pass

    if (len(page_content.strip()) > int(config['minContent'])):
        try:
            with open("%s-%s.html" % (tid, title), 'w+', encoding='utf-8', errors='ignore') as file:
                file.write(
                    '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE html><html><head><META HTTP-EQUIV="content-type" CONTENT="text/html; charset=utf-8">  <title>')
                file.write(title)
                file.write("</title></head><body><pre><p>")
                file.write(page_content)
                file.write("</p></pre></body></html>")
                print('Done')
        except:
            print("Error writing %s" % title)


def extract_title(content):
    title_left = content.find('<title>')+len('<title>')
    title_right = content.find('</title>')
    title = content[title_left:title_right]

    title_search = re.search('[【《](.*)[】》]', title, re.IGNORECASE)
    if title_search:
        title = title_search.group(1)
    else:
        title = title.replace(" - cool18.com", "").strip()
    return title


def loadConfig():
    cf = configparser.ConfigParser()
    try:
        cf.read('c2epub.conf')
        config['enableProxy'] = cf.get('network', 'enableProxy')
        config['proxy'] = cf.get('network', 'proxy')
        config['minContent'] = cf.get('config', 'minContent')
        config['waitPackage'] = cf.get('config', 'waitPackage')
    except:
        pass


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print('a cool18.com url is required')
        exit()
    pypath = sys.argv[0]
    loadConfig()

    src = fetch(sys.argv[1])
    title = extract_title(src)
    try:
        with open("%s.ini" % title, 'w+', encoding='utf-8', errors='ignore') as file:
            file.write("TITLE: %s \r\n" % title)
            file.write("URL: %s \n" % sys.argv[1])
    except:
        pass

    try:
        os.mkdir(title)
    except:
        pass
    finally:
        os.chdir(title)

    hive = [sys.argv[1]]

    downloaded = set()
    while hive:
        current_url = hive.pop()
        if (current_url in downloaded):
            print("Ignore %s " % current_url)
        else:
            print("[%d]Download: %s" % (len(hive), current_url))
            downloaded.add(current_url)
            download(current_url)
    if config['waitPackage'] == 'yes':
        input('Press Enter when ready...')

    dirname = os.path.dirname(os.path.realpath(__file__))
    print("Download completed, now packaging epub...")
    epub = html2epub.Epub(title)
    for file in os.listdir("."):
        chap = html2epub.create_chapter_from_file(file)
        epub.add_chapter(chap)
    epub.create_epub(dirname)
    print("OK")
