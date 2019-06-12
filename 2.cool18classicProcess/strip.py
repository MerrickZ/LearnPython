import sys,os

f=open(sys.argv[1],'r',errors='ignore')
fid = f.name.split('.')[0]
c=f.read()
f.close()

#extract title
title_left=c.find('<title>')+len('<title>')
title_right=c.find('</title>')
title=c[title_left:title_right]

#extract content
c_left=c.find("<!--bodybegin-->")+len("<!--bodybegin-->")
c_right=c.rfind("<!--bodyend-->")
if (c_left>15 and c_right>c_left) :
    c=c[c_left:c_right]
else :
    c_left=c.find("</head>")+len("</head>")
    c_right=c.rfind("</body>")
    c=c[c_left:c_right]

import bs4
soup=bs4.BeautifulSoup(c,'lxml')
for a in soup.find_all('font'): 
    a.clear()
f=open(fid+title+".txt",'w+',errors='ignore')
content=soup.get_text(separator="\n")
f.write(content)
f.close()

os.remove(sys.argv[1])
