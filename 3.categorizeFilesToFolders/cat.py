import os,sys,re,shutil
def get_fileNamex(filename):
    (filepath,tempfilename) = os.path.split(filename);
    (shotname,extension) = os.path.splitext(tempfilename);
    return filepath,shotname,extension


def movefile(filename) :
    filepath,shortname,ext=get_fileNamex(filename)
    plainname = filename[filename.find('-')+1:-4]

    mark=0
    title=""

    for i in range(2,len(plainname)):
        if plainname[i] in ("("," ","（","-","之","第","0","1","2","3","4","5","6","7","8","9","－","一","二","三","四","五","六","七","八","九","十","—") :
            mark=i
            break

    if (mark == 0) :
        title=plainname
    else :
        title=plainname[:mark]

    try:
        os.mkdir(title)
    except IOError :
        pass

    shutil.move(filename,"."+filepath+"/"+title+"/"+shortname+ext)


path = os.getcwd()
if (len(sys.argv) >1) :
    path = sys.argv[1]

files = os.listdir(path)
for i in files :
    if (i.endswith(".txt")) :
        movefile(i)
