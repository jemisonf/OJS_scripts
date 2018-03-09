from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from PyPDF2 import PdfFileWriter, PdfFileReader
from cStringIO import StringIO
from parse_file import articleToXml, bookReviewToXml 
from pdf_to_text import convert_pdf_to_txt
from lxml import etree
from split_article import split_article
import sys

def getIssueData():
    data = {}
    print("Journal Information #####################")
    data["volume"] = raw_input("Enter the volume for this journal: ")
    data["number"] = raw_input("Enter the number for this journal: ")
    data["year"] = raw_input("Enter the year for this journal: ")
    data["date_published"] = raw_input("Enter the date published for this journal: ")
    data["access_date"] = raw_input("Enter the access date for this journal: ")
    print("End Journal Information #################\n")
    return data
    
def main():
    if (len(sys.argv) > 1):
        baseEl = etree.Element('issue', published="true", current="false")
        issueData = getIssueData()
        etree.SubElement(baseEl, 'title').text = '0'
        etree.SubElement(baseEl, 'volume').text = issueData["volume"]
        etree.SubElement(baseEl, 'number').text = issueData["number"]
        etree.SubElement(baseEl, 'year').text = issueData["year"]
        etree.SubElement(baseEl, 'date_published').text = issueData["date_published"]
        etree.SubElement(baseEl, 'access_date').text = issueData["access_date"]
        articlesEl = etree.SubElement(baseEl, 'section')
        etree.SubElement(articlesEl, 'title', locale="en_US").text = 'Articles'
        etree.SubElement(articlesEl, 'abbr', locale="en_US").text = 'ART'
        while(True):
            print("Article information ####################\n")
            articleName = raw_input("What is the article name? You can enter a temporary filename if you want.")
            articleStart = raw_input("What is the start page of this article? ")
            while(not articleStart.isdigit()):
                articleStart = raw_input("Please enter an integer. What is the start page of this article? ")
            articleEnd = raw_input("What is the end page of this article? ")
            while(not articleEnd.isdigit()):
                articleEnd = raw_input("Please enter an integer. What is the end page of this article? ")
            articleText = convert_pdf_to_txt(sys.argv[1], int(articleStart), int(articleEnd))
            split_article(sys.argv[1], articleName, int(articleStart), int(articleEnd))
            articleBinary = open(articleName, "rb").read().encode("base64")
            articleXml = articleToXml(articleText, articleName, articleBinary, issueData["date_published"])
            articlesEl.insert(-1, articleXml)
            if (raw_input("Parse another article? Type yes to continue or any other character to quit. ") != "yes"):
                break
   
        if (raw_input("Are there book reviews to parse? Type yes to continue. ")):
            bookReviewsElement = etree.SubElement(baseEl, 'section')
            etree.SubElement(bookReviewsElement, 'title', locale="en_US").text = 'Book Reviews'
            etree.SubElement(bookReviewsElement, 'abbr', locale="en_US").text = 'BKRV'
            while(True):
                articleName = raw_input("What is the article name? You can enter a temporary filename if you want.")
                articleStart = raw_input("What is the start page of this article? ")
                while(not articleStart.isdigit()):
                    articleStart = raw_input("Please enter an integer. What is the start page of this article? ")
                articleEnd = raw_input("What is the end page of this article? ")
                while(not articleEnd.isdigit()):
                    articleEnd = raw_input("Please enter an integer. What is the end page of this article? ")

                split_article(sys.argv[1], articleName, int(articleStart), int(articleEnd))
                articleBinary = open(articleName, "rb").read().encode("base64")
                articleXml = bookReviewToXml(articleText, articleName, articleBinary, issueData["date_published"])
                bookReviewsElement.insert(-1, articleXml)
                if (raw_input("Parse another article? Type yes to continue or any other character to quit. ") != "yes"):
                    break

        tree = etree.ElementTree(baseEl)
        tree.write('output.xml', pretty_print=True)

    else:
        print "Not enough input entered"


main()


