import os
import shutil
import stat
import sys

from PyPDF2 import PdfFileReader, PdfFileWriter


def deletepagesFromPdf(pdfin, pdfout):
    with open(pdfin, 'rb') as f:
        pdf_src = PdfFileReader(f)
        ipages = pdf_src.getNumPages()
        print("Original PDF Pages: %d" % ipages)
        skip_page_1 = False
        skip_page_last = False

        page2detect_1st = pdf_src.getPage(1)
        if page2detect_1st.mediaBox[2] == 960 and page2detect_1st.mediaBox[3] == 540:
            skip_page_1 = True
        page2detect_2nd = pdf_src.getPage(ipages-1)
        print("mediabox %s" % page2detect_2nd.mediaBox)
        if page2detect_2nd.mediaBox[2] == 294.24 and page2detect_2nd.mediaBox[3] == 206.4:
            skip_page_last = True

        pdf_out = PdfFileWriter()
        pdf_out.addPage(pdf_src.getPage(0))
        fromindex = 1
        toindex = ipages-1
        if skip_page_1:
            fromindex = 2
        if skip_page_last:
            toindex = ipages-2
        for i in range(fromindex, toindex):
            pdf_out.addPage(pdf_src.getPage(i))
        with open(pdfout, 'wb') as fo:
            pdf_out.write(fo)


if __name__ == '__main__':
    print('清理当前目录下的PDF文件')
    current_dir = os.path.dirname(sys.argv[0])
    os.chdir(current_dir)
    files = [f for f in os.listdir(current_dir) if (".pdf" in f)]

    for f in files:
        print("处理文件： %s" % f)
        os.chmod(f, stat.S_IWRITE)
        try:
            if "2019" in f:
                deletepagesFromPdf(current_dir+"/"+f, current_dir+"/2019/"+f)
            if "2018" in f:
                deletepagesFromPdf(current_dir+"/"+f, current_dir+"/2018/"+f)
            if "2017" in f:
                deletepagesFromPdf(current_dir+"/"+f, current_dir+"/2017/"+f)
            if "2016" in f:
                deletepagesFromPdf(current_dir+"/"+f, current_dir+"/2016/"+f)
            if "2015" in f:
                deletepagesFromPdf(current_dir+"/"+f, current_dir+"/2015/"+f)
            os.remove(f)
        except Exception as e:
            print("处理失败 %s" % e)
