import xml.etree.ElementTree as etree
import sys

# This produces a full description of the elements given in a Schema definition.
# I.e. given a primary XSD, which possibly includes others, this will search for all elements and their descriptions.

def searchIncludes(NS, typename):
    hit = None
    for key in inclroots:
        res = inclroots[key].findall(NS + 'complexType[@name="' + typename + '"]')
        if len(res) > 0:
            hit = res

        res = inclroots[key].findall(NS + 'simpleType[@name="' + typename + '"]')
        if len(res) > 0:
            hit = res

    return hit
 
def parsefile(node, indent=''):
    for child in node:
        if child.tag == NS+'element':
            display=[' ']
            for attr in ['minOccurs', 'maxOccurs']:
                if attr in child.attrib:
                    display.append(attr+':'+child.attrib[attr])
            print(indent + child.attrib['name'] + ' '.join(display))
            typenode = searchIncludes(NS, child.attrib['type'])

            if typenode is not None:
                parsefile(typenode, indent+'  ')
        elif child.tag == NS+'restriction':
            if showrestrictions:
                print(indent, child.attrib['base'])
            parsefile(child, indent+'  ')
        elif child.tag in [NS+'minLength', NS+'maxLength', NS+'pattern']:
            if showrestrictions:
                print(indent, child.tag, child.attrib['value'])
        else:
            parsefile(child, indent+'  ')
###############################

# The main file:
xsdfilename = 'IE4N10.xsd'
# This contains the namespace of the XSD, not the targetnamespace of the XML specified by the XSD:
NS = '{http://www.w3.org/2001/XMLSchema}'
# The files that are included by the main file, and also any that are included by an include file:
includefiles = ['ctypes.xsd', 'htypes.xsd', 'stypes.xsd']

showrestrictions = True

# Parse the main file.
tree = etree.parse(xsdfilename)
root = tree.getroot()

# Parse the includefiles, and store their respective roots
# under the filename.
inclroots = {}
for inclfile in includefiles:
    print('Including ' + inclfile)
    inclroots[inclfile] = etree.parse(inclfile).getroot()

parsefile(root)
