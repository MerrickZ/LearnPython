import requests
import bs4
import sys,os

def download(url) :
    if (url.find("cool18.com")<0) :
        return
    
    #Change to your own proxy.
    #Requires PySocks
    proxy='socks5://127.0.0.1:1081'
    proxies=dict(http=proxy,https=proxy)

    P_START="<!--bodybegin-->"
    P_END="<!--bodyend-->"
    L_START='''<a name="followups" style=''>'''
    L_END='''<a name="postfp">'''
    
    resp = requests.get(url, proxies=proxies)
    src = resp.content.decode('utf-8')

    title_left=src.find('<title>')+len('<title>')
    title_right=src.find('</title>')
    title=src[title_left:title_right]
    title=title.replace(" - cool18.com","").strip()
    print('>>> %s' % title )
    
    raw = str(src)

    try:
        pos_start = raw.find(P_START)+len(P_START)
        pos_end = raw.find(P_END)
        page_content = raw[pos_start:pos_end]
        content_soup = bs4.BeautifulSoup(page_content,"lxml")
        #Other chapters
        links = content_soup.find_all('a')
        for a in links :
            _url = a.get('href')
            if (_url and len(_url.strip())>8) :
                hive.append(_url)
            a.clear()
    except ValueError:
        return

    try :
        lpos_start = raw.find(L_START)+len(L_START)
        lpos_end = raw.find(L_END)
        comments = raw[lpos_start:lpos_end]
        comm_soup=bs4.BeautifulSoup(comments,"lxml")
        for a in comm_soup.find_all('a'):
            _u = a.get('href')
            if (_u and _u.startswith("http")) :
                hive.append(_u)
            else:
                hive.append('https://www.cool18.com/bbs4/%s' % _u)
    except ValueError:
        pass
    
    page_content = content_soup.getText(strip=True,separator="\n").replace('cool18.com','\n').replace('www.6park.com','').replace('6park.com','')
    try:
        last_pos=page_content.rindex('评分完成')
        page_content = page_content[:last_pos]
    except ValueError :
        pass

    if (len(page_content.strip())>100) :
        try:
            with open("%s.txt" % title,'w+',encoding='utf-8',errors='ignore') as file :
                file.write(page_content)
                print('Done')
        except :
            print("Error writing %s" % title)
   

if __name__ == '__main__':
    if (len(sys.argv)<2) :
        print('a cool18.com url is required')
        exit()
    pypath = sys.argv[0]

    proxy='socks5://127.0.0.1:1081'
    proxies=dict(http=proxy,https=proxy)
    resp = requests.get(sys.argv[1], proxies=proxies)
    src = resp.content.decode('utf-8')
    
    title_left=src.find('<title>')+len('<title>')
    title_right=src.find('</title>')
    title=src[title_left:title_right]
    title=title.replace(" - cool18.com","").strip()
    
    os.mkdir(title)
    os.chdir(title)
    
    hive = [sys.argv[1]]
    downloaded = set()
    while (len(hive)>0) :
        current_url = hive.pop()
        if (current_url in downloaded) :
            print("Ignore")
        else :
            print("[%d]Download: %s" % (len(hive),current_url))
            downloaded.add(current_url)
            download(current_url)
        
