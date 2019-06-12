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
    soup = bs4.BeautifulSoup(src,"html.parser")
    title = soup.title.get_text()[:-13]
    print('>>> %s' % title )
    
    raw = str(src)

    try:
        pos_start = raw.index(P_START)+len(P_START)
        pos_end = raw.index(P_END)
        page_content = raw[pos_start:pos_end]
        content_soup = bs4.BeautifulSoup(page_content,"html.parser")
        #Other chapters
        links = content_soup.find_all('a')
        for a in links :
            hive.append(a['href'])
    except ValueError:
        return

    try :
        lpos_start = raw.index(L_START)+len(L_START)
        lpos_end = raw.index(L_END)
        comments = raw[lpos_start:lpos_end]
        comm_soup=bs4.BeautifulSoup(comments,"html.parser")
        for a in comm_soup.find_all('a'):
            hive.append('https://www.cool18.com/bbs4/%s' % a['href'])
    except ValueError:
        pass
    
    #Remove in page links
    for i in content_soup.findAll('a') :
        i.clear()

    page_content = content_soup.getText(strip=True).replace('cool18.com','\n')
    try:
        last_pos=page_content.rindex('评分完成')
        page_content = page_content[:last_pos]
    except ValueError :
        pass

    if (len(page_content.strip())>100) :
        file = open("%s.txt" % title,'w+',encoding='utf-8')
        file.write(page_content)
        file.close()
        print('Done')

if __name__ == '__main__':
    if (len(sys.argv)<2) :
        print('a cool18.com url is required')
        exit()
    pypath = sys.argv[0]

    proxy='socks5://127.0.0.1:1081'
    proxies=dict(http=proxy,https=proxy)
    resp = requests.get(sys.argv[1], proxies=proxies)
    src = resp.content.decode('utf-8')
    soup = bs4.BeautifulSoup(src,"html.parser")
    title = soup.title.get_text()[:-13]
    
    os.mkdir(title)
    os.chdir(title)
    
    hive = [sys.argv[1]]
    downloaded = set()
    while (len(hive)>0) :
        current_url = hive.pop()
        if (current_url in downloaded) :
            print("Pass")
        else :
            print("Queue[%d]：%s" % (len(hive),current_url))
            downloaded.add(current_url)
            download(current_url)
        
