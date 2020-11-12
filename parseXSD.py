import xml.etree.ElementTree as etree
import sys
import datetime

# This produces a full XML-file with all elements given in a Schema definition.
# Also adds minOccurs and maxOccurs to element, and the restrictions, maxlength, minlength and pattern, if any.
# I.e. given a primary XSD, which possibly includes others, this will search for all elements and their descriptions.
# Should I check for targetnamespace(s)?

#--------------------------------------------------------------------------------------------------
def writeFile(string, filename):
    f = open(filename, "w", encoding="utf-8")
    f.write(string)
    f.close()

# Search include files for a given type name.
# Should I check for duplicate definitions?
# I use find i.s.o. findall, because the return value suits me:
# When iterating over this result, I get the children of the found node, where as
# iterating over the result of findall first goes through the found node itself.
def searchIncludes(NS, typename):
    for key in xsdroots:
        res = xsdroots[key].find(NS + 'complexType[@name="' + typename + '"]')
        if res is not None:
            return res
        res = xsdroots[key].find(NS + 'simpleType[@name="' + typename + '"]')
        if res is not None:
            return res

    print('NB: type ', typename, ' not found.')
    return None


# Skip these (complexType and simpleType) because they are found above in searchIncludes. If the type is defined in same file as the element, it will appear twice...
def parsefile(node, newxml, indent=''):
    if node is None:
        return

    for child in node:
        if child.tag == NS+'element':
            if 'ref' in child.attrib or 'name' not in child.attrib:
                print(child.tag, child.attrib, '"ref" used or "name" missing. Quitting.')
                sys.exit()

            childxml = etree.SubElement(newxml, child.attrib['name'])

            for attr in ['minOccurs', 'maxOccurs', 'nillable']:
                if attr in child.attrib and showrestrictions:
                    childxml.set(attr, child.attrib[attr])

            if 'type' in child.attrib:
                typenode = searchIncludes(NS, child.attrib['type'])
                parsefile(typenode, childxml, indent+'  ')
            else:
                parsefile(child, indent+'  ')
        elif child.tag == NS+'restriction':
            if showrestrictions:
                newxml.text = child.attrib['base']
            parsefile(child, newxml, indent+'  ')
        elif child.tag in [NS+'minLength', NS+'maxLength', NS+'pattern']:
            if showrestrictions:
                if newxml.text is not None:
                    newxml.text = newxml.text + ' ' + child.attrib['value']
                else:
                    newxml.text = child.attrib['value']
        elif child.tag.endswith('Type'):
            # Skipping TYPE: Already processed via searchIncludes.
            continue
        else:
            parsefile(child, newxml, indent+'  ')

###############################

# The root element:
rootelementname = 'IE4N10'        # Used in the filename.

# This contains the namespace of the XSD, not the targetnamespace of the XML specified by the XSD:
NS = '{http://www.w3.org/2001/XMLSchema}'

# All xsd files describing this xml.
# NB: Primary file must come first.
xsdfiles = ['IE4N10.xsd', 'ctypes.xsd', 'htypes.xsd', 'stypes.xsd']

showrestrictions = True

# Parse the xsd files, and store their respective roots
# under the filename.
xsdroots = {}
for file in xsdfiles:
    xsdroots[file] = etree.parse(file).getroot()

mainroot = xsdroots[xsdfiles[0]]
if mainroot.tag == NS+'schema' and 'targetNamespace' in mainroot.attrib:
    tns = mainroot.attrib['targetNamespace']
    print('TNS=' + tns)

newxml = etree.Element('dummyroot')
parsefile(mainroot, newxml)
xmlfilename = rootelementname + '.v2.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xml'
writeFile('<?xml version="1.0" encoding="utf-8"?>' + etree.tostring(newxml, encoding="unicode"), xmlfilename)
print('Saved to file ' + xmlfilename)
