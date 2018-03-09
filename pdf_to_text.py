from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

# from https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python

# input: 
#   path: a string representing to path to a pdf file to be decoded
# output:
#   text: a utf-8 encoded string representing the text in the first 3 pages of the pdf file at path
# preconditions: path should  be a valid path to a valid pdf. Program may fail if the pdf cannot be parsed.
#   may not handle pdfs where text has been rotated. See the stack overflow link for a potential fix.
# postconditions: text will be utf-8 encoded. The contents of text will not have been parsed or edited in any way from the raw data.
def convert_pdf_to_txt(path, start_page=None, end_page=None):
    print('parsing filename: ' + path)
    if (start_page == None):
        start_page = 1;
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = end_page
    caching = True
    pagenos=set()
    pages = PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True)
    for i, page in enumerate(pages):
        if (i >= start_page - 1):
            interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    return text.decode('utf-8')
