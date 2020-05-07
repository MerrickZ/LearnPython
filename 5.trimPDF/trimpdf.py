import os
import shutil
import stat
import sys

from PyPDF2 import PdfFileReader, PdfFileWriter

#########################################
# Author: MerrickZ (anphorea@gmail.com) #
#########################################

# This script is used to remove some ad pages from PDFs by verifing the page height and width.

def deletepagesFromPdf(pdfin, pdfout):
    print(f"{pdfin} --> {pdfout}")
    pdf_writer = PdfFileWriter()
    pdf_reader = PdfFileReader(pdfin)
    ipages = pdf_reader.getNumPages()
    print(f"Original PDF Pages: {ipages}")
    for i in range(ipages):
        page_src = pdf_reader.getPage(i)
        if (page_src.mediaBox[2] == 960) and (page_src.mediaBox[3] == 540):
            continue
        if (page_src.mediaBox[2] == 294.24) and (page_src.mediaBox[3] == 206.4):
            continue
        pdf_writer.addPage(page_src)
    print(f"New PDF Pages: {pdf_writer.getNumPages()}")
    if pdf_writer.getNumPages() + 2 < ipages:
        # all same size, leave it be.
        return
    with open(pdfout, 'wb') as o:
        pdf_writer.write(o)
    os.remove(pdfin)


def sort_into_directories(cdir, filename):
    years = ["2020", "2019", "2018", '2017', '2016', '2015']
    for i in years:
        if i in filename:
            if (not os.path.exists(i)):
                os.mkdir(i)
            deletepagesFromPdf(filename, os.path.join(cdir, i, filename))
            return


if __name__ == '__main__':
    print('清理当前目录下的PDF文件')
    current_dir = os.path.dirname(sys.argv[0])
    os.chdir(current_dir)
    files = [f for f in os.listdir(current_dir) if (".pdf" in f)]

    for f in files:
        print("处理文件： %s" % f)
        os.chmod(f, stat.S_IWRITE)
        try:
            sort_into_directories(current_dir, f)
        except Exception as e:
            print("处理失败 %s" % e)
