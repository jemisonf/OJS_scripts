import sys
import re
# import xml.etree.cElementTree as etree
from lxml import etree

author_line_regex = re.compile(r"by ((\s?.+) ((.+ )?(.+),($)?)+ and ((.+) (.+ )?(.+$))| ?(.+) ((.+ )?)((.+))$|(\s?((\w|-)+\s)(((\w|-)+\W\s)?)((\w|-)+) and (((\w|-)+\s)(((\w|-)+\W\s)?)((\w|-)+))))")
multi_lines_author_regex = re.compile("by (\s?(\w+\s)((\w+\W\s)?)(\w+),($)?)")
introduction_regex = re.compile("(introduction)|(background)", re.IGNORECASE)

# input: 
#   line: a string containing text that describes the authors of an article
# output:
#   authors: an array of hashes, each corresponding to one author of the piece. 
#   formatted as: {
#                   "firstname": ...
#                   "middlename": ...
#                   "lastname": ...
#                 }
# preconditions: line should match one of the following formats:
#   (1). by Firstname Lastname
#   (2). by Firstname Lastname and Other Person
#   (3). by Firstname Lastname, Person Two, and Person Three
#       - names can also be written as Firstname H. Lastname (middle initial followed by a period)
# postconditions: returns an array of authors. This function is fairly robust and generally won't crash if it's given invalid data, but it will return invalid information.
#   If the function returns invalid information, the resulting xml will generate incorrectly, but it isn't very hard to fix.
#   Always read over the final xml file to make sure your data has been parsed correctly.
def parse_authors(line):
    line = line.strip()
    arr = re.split(r" |\n", line)
    authors = []
    arr.pop(0) # remove "by"
    newAuth = {}
    while (len(arr) > 1):
        tempVal = arr.pop(0).encode('utf-8')
        while (len(tempVal) == 0 or tempVal == 'and'): # ignore irrelevant words
            tempVal = arr.pop(0).encode('utf-8')
        newAuth["firstname"] = tempVal # assume current val is the first name
        tempVal = arr.pop(0)
        if (tempVal[-1] == '.' or tempVal[-1] == ')'): # assumes only middle names are initials or alternative first names -- needs tweaking
            newAuth["middlename"] = tempVal
            tempVal = arr.pop(0).encode('utf-8')
        else:
            newAuth["middlename"] = ''
        newAuth["lastname"] = tempVal.rstrip(',') # last name is the next word, needs to have last comma stripped from end
        authors.append(newAuth) # add generated author to list of authors
        print ("Added " + newAuth["firstname"] + " " + newAuth["lastname"])
        newAuth = {} # clear newAuth
    return authors

# input:
#   raw_title: a string of title data pulled directly from the pdf text
# output:
#   title: raw_title with extraneous characters removed
# preconditions: title should be a string
# postconditions: title will have new lines and leading/trailing white space removed
def getFormattedTitle(raw_title):
    title = raw_title.replace('\n', '').strip()
    return title

# input:
#   raw_abstract: a string of title data pulled directly from the pdf text
# output:
#   title: raw_abstract with extraneous characters removed
# preconditions: abstract should be a string
# postconditions: abstract will have new lines, tab characters and leading/trailing white space removed. Double spaces will be replaced with single spaces.
def getFormattedAbstract(raw_abstract):
    abstract = raw_abstract.replace('\n', '').replace('\t', ' ').replace('  ', ' ').strip()
    return abstract

# input: 
#   string: the raw text of the pdf to be parsed
# output:
#   data: a hash map containing "title", the title of the article, "names", the names of the writers (see parse_authors for more info) and "abstract", the formatted abstract
# preconditions: string must be the raw text of a pdf. Should follow this general format:
#       [title -- can be multiple lines]
#       [authors -- see parse_authors for format info. Should be 1-2 lines]
#       [abstract -- can be multiple lines]
#       Introduction [this is ignored but is used as a stopping place when parsing the abstract]
#       ...
def parseString(string):
    lines = string.splitlines()
    counter = 0
    title = ""
    abstract = ""
    names = []
    while True: # add each line to title until the line describing the authors is reached
        if (multi_lines_author_regex.match(lines[counter])): # if author list takes up two lines, parse two lines
            authors = lines[counter]
            authors += lines[counter + 1]
            names = parse_authors(authors)
            counter += 2
            break
        if (author_line_regex.match(lines[counter])): # otherwise if author list takes on up line, only parse current line
            names = parse_authors(lines[counter])
            counter += 1
            break
        else:
            title += lines[counter]
        counter += 1
    while (not introduction_regex.match(lines[counter]) and counter < 30): # add all subsequent lines to abstract until line reads "Introduction"
        abstract += lines[counter]
        counter += 1
    title = getFormattedTitle(title)
    abstract = getFormattedAbstract(abstract)
    return ({ "title": title, "names": names, "abstract": abstract })

# input:
#   data: the values returned from parseString
#   binary: a pdf document encoded in base64
#   filename: the name of the pdf file being parsed
# output:
#   an xml <article> element with children set up according to the template.xml file from Confluence
#       Ex:
#           <article>
#               <title locale="en_US">data["title"]</title>
#               <abstract locale="en_US">data["abstract"]</abstract>
#               <author primary_contact="true">data["authors"][0]</author>
#                   <firstname>Firstname</firstname>
#                   <middlename>></middlename>
#                   <lastname>Lastname</lastname>
#                   <affiliation>[USER INPUT]</affiliation>
#                   <email>no@email.com</email>
#               </author>
#               <date_published></date_published>
#               <galley locale="en_US">
#                   <label>PDF</label>
#                   <file>
#                       <embed filename=filename encoding="base64">
#                           ...
#                       </embed>
#                   </file>
#               </galley>
#           </article>
# preconditions: all values should be valid and correspond to the same file.
# postconditions: probably will not fail unless a value isn't entered. 
#   However, if invalid data is submitted for binary or filename, it's possible the upload won't work.
def getXml(data, binary, filename, date, sectionName):
    print "Parsing " + data["title"]
    rootSection = etree.Element(sectionName)
    articles = []
    etree.SubElement(rootSection, 'title', locale="en_US").text = data["title"]
    if data.has_key("abstract"):
        etree.SubElement(rootSection, 'abstract', locale="en_US").text = data["abstract"]
    for author in data['names']:
        try:
            affiliation = raw_input (u"What is the affiliation of " + author["firstname"] + u' ' + author["lastname"] + u'? ')
        except:
            affiliation = raw_input ("Can't display name of author. What is their affiliation? ") # some names include unicode characters. I didn't want to figure out a solution so I added this try/catch block
        if (author == data['names'][0]):
            authorEl = etree.SubElement(rootSection, 'author', primary_contact="true") # the first author needs to be designated the primary contact
        else:
            authorEl = etree.SubElement(rootSection, 'author')
        etree.SubElement(authorEl, 'firstname').text = author['firstname']
        etree.SubElement(authorEl, 'middlename').text = author['middlename']
        etree.SubElement(authorEl, 'lastname').text = author['lastname']
        etree.SubElement(authorEl, 'affiliation').text = affiliation
        etree.SubElement(authorEl, 'email').text = 'no@email.com' # I could never find an email for any author listed in the paper
    etree.SubElement(rootSection, 'date_published').text = date
    galley = etree.SubElement(rootSection, 'galley', locale='en_US')
    etree.SubElement(galley, 'label').text = 'PDF'
    file = etree.SubElement(galley, 'file')
    # sometimes pdfs will contain null bytes or special characteres and fail to upload
    try:
        etree.SubElement(file, 'embed', filename=filename, encoding="base64", mime_type="application/pdf").text = binary
    except:
        # if this fails, remove the galley section
        # article will upload and you can add the pdf manually
        print "Could not parse binary for " + data["title"] + ". You should correct this after uploading."
        rootSection.remove(galley)
    return rootSection

def bookReviewToXml(fileText, filename, fileBinary, date):
    num_authors_input = ""
    authors = []
    data = {}
    while (not num_authors_input.isdigit()):
        newAuth = {}
        num_authors_input = raw_input("How many authors does this piece have? ")
    for i in range(int(num_authors_input)):
        user_input = raw_input("What is the author's name (firstname lastname or firstname middlename lastname)? ") 
        newAuth["firstname"] = user_input.split(' ')[0]
        if (len(user_input.split(' ')) == 2):
            newAuth["lastname"] = user_input.split(' ')[1]
        else:
            newAuth["middlename"] = user_input.split(' ')[1]
            newAuth["lastname"] = user_input.split(' ')[2]
        authors.append(newAuth)
    data["names"] = authors
    data["title"] = raw_input("What is the title of the review? ")
    xml = getXml(data, fileBinary, filename, date, "article")
    return xml

    
# input: 
#   fileText: the raw text of a pdf file
#   filename: the name of pdf file being processed
#   fileBinary: the base64 encoded data for the file being uploaded (is this actually binary? I'm not sure)
#   date: the publish date of the article
# output: 
#   xml: the xml file outputted from getXml based on data from parseString and params
# preconditions: all params should refer to the same file. fileText should follow format specifications from parseString
# postconditions: will return synactically valid xml. Errors are not handled if invalid data is submitted. If author names deviate from specifications in parse_authors, you will need to correct the output xml
def articleToXml(fileText, filename, fileBinary, date):
    stringOutput = parseString(fileText)
    xml = getXml(stringOutput, fileBinary, filename, date, "article")
    return xml

