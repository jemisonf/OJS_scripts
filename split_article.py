from PyPDF2 import PdfFileWriter, PdfFileReader

# input:
#   journal: the name of the file containing the journal to be parsed
#   fileName: the name of the file the function should write to
#   startPage: the page number where the split should begin (this will be included in the output)
#   endPage: the page number where the split should end (this will be included in the output)
# preconditions:
#   journal should be a real pdf file
#   fileName should be a non-empty string
#   startPage should be less than or equal to endPage and greater than 0
#   endPage should be greater than or equal to startPage and less than or equal to the number of pages in the document
#   the "first" page is page 1, not page 0 -- if the split starts at the beginning of the document and ends on the 3rd page, then startPage=1 and endPage=3
#       **NOT startPage=0 and endPage=2**
#       This is to allow startPage and endPage to be taken directly from user input
# postconditions:
#   this function will write the split pdf to a file with the name [fileName] in the local directory
#   if [fileName] already contains information, it will be overwritten

def split_article(journal, fileName, startPage, endPage):
    fullPdf = PdfFileReader(open(journal, "rb"))
    output = PdfFileWriter()
    for i in range(fullPdf.numPages):
        if (i + 1 >= startPage and i + 1 <= endPage):
            output.addPage(fullPdf.getPage(i))
    outputStream = file(fileName, "wb")
    output.write(outputStream)
    outputStream.close()
