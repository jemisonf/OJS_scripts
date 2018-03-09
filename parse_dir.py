from parse_file import articleToXml
from pdf_to_text import convert_pdf_to_txt
from lxml import etree
import sys

def getIssueData():
    data = {}
    print 
    data["volume"] = raw_input("Enter the volume for this journal: ")
    data["number"] = raw_input("Enter the number for this journal: ")
    data["year"] = raw_input("Enter the year for this journal: ")
    data["date_published"] = raw_input("Enter the date published for this journal: ")
    data["access_date"] = raw_input("Enter the access date for this journal: ")
    return data
    

def main():
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
    if (len(sys.argv) > 1):
        for file in sys.argv[1: ]: # add an article tag for each file
            fileText = convert_pdf_to_txt(file)
            fileBinary = open(file, "rb").read().encode("base64")
            fileXml = articleToXml(fileText, file, fileBinary, issueData["date_published"])
            articlesEl.insert(-1, fileXml)
    tree = etree.ElementTree(baseEl)
    tree.write('output.xml', pretty_print=True) # write end result to 'output.xml'


main()
