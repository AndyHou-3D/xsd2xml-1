import xml.etree.ElementTree as etree
import sys
import datetime

# This produces a full description of the elements given in a Schema definition.
# I.e. given a primary XSD, which possibly includes others, this will search for all elements and their descriptions.
# Should I check for multiple targetnamespaces?

#--------------------------------------------------------------------------------------------------
def writeFile(string, filename):
    f = open(filename, "w", encoding="utf-8")
    f.write(string)
    f.close()

# Search include files for a given type name.
# Should I check for duplicate definitions?
def searchIncludes(NS, typename):
    for key in xsdroots:
        res = xsdroots[key].findall(NS + 'complexType[@name="' + typename + '"]')
        if len(res)>0:
            return res
        res = xsdroots[key].findall(NS + 'simpleType[@name="' + typename + '"]')
        if len(res)>0:
            return res

    print('NB: type ', typename, ' not found.')
    return None
 
def parsefile(node, parent, indent=''):
    for child in node:
        if child.tag == NS+'element':
            if 'ref' in child.attrib or 'name' not in child.attrib:
                print(child.tag, child.attrib, '"ref" used or "name" missing. Quitting.')
                sys.exit()

            childxml = etree.SubElement(parent, child.attrib['name'])
            display=[' ']
            for attr in ['minOccurs', 'maxOccurs']:
                if attr in child.attrib:
                    childxml.set(attr, child.attrib[attr])

            if 'type' not in child.attrib:
                parsefile(child, childxml, indent+'  ')
            else:
                typenode = searchIncludes(NS, child.attrib['type'])
                if typenode is not None:
                    parsefile(typenode, childxml, indent+'  ')
        elif child.tag == NS+'restriction':
            if showrestrictions:
                parent.text = child.attrib['base']
            parsefile(child, parent, indent+'  ')
        elif child.tag in [NS+'minLength', NS+'maxLength', NS+'pattern']:
            if showrestrictions:
                if parent.text is not None:
                    parent.text = parent.text + ' ' + child.attrib['value']
                else:
                    parent.text = child.attrib['value']
        else:
            parsefile(child, parent, indent+'  ')

    return parent

###############################

# The root element:
rootelementname = 'IE4N10'
rootelementtype = 'IE4N10Type'
# This contains the namespace of the XSD, not the targetnamespace of the XML specified by the XSD:
NS = '{http://www.w3.org/2001/XMLSchema}'
# All xsd files describing this xml:
xsdfiles = ['IE4N10.xsd', 'ctypes.xsd', 'htypes.xsd', 'stypes.xsd']

showrestrictions = True

# Parse the xsd files, and store their respective roots
# under the filename.
xsdroots = {}
for file in xsdfiles:
    print('Adding ' + file)
    xsdroots[file] = etree.parse(file).getroot()

newxml = etree.Element(rootelementname)
rootnode = xsdroots[xsdfiles[0]].findall(NS + 'complexType[@name="' + rootelementtype + '"]')
if len(rootnode) == 1:
    parsefile(rootnode[0], newxml)
    xmlfilename = rootelementname + '.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xml'
    writeFile('<?xml version="1.0" encoding="utf-8"?>' + etree.tostring(newxml, encoding="unicode"), xmlfilename)
else:
    print('No root node: Name= ' + rootelementname + ' Type=' + rootelementtype)

