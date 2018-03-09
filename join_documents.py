from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
import sys

def main():
    merger = PdfFileMerger()
    if (len(sys.argv) > 1):
        for file in sys.argv[1: ]:
            merger.append(open(file, "rb"))
    merger.write("result.pdf")

main()

