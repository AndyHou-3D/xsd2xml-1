import xml.etree.ElementTree as etree
import sys
import datetime

# This produces a full XML-file with all elements given in a Schema definition.
# Also adds minOccurs and maxOccurs to element, and the restrictions, maxlength, minlength and pattern, if any.
# I.e. given a primary XSD, which possibly includes others, this will search for all elements and their descriptions.
# Should I check for targetnamespace(s)?

#--------------------------------------------------------------------------------------------------
def search4Includes(files):
    root = etree.parse(files[len(files)-1]).getroot()
    includes = root.findall('.//'+NS+'include')
    
    for inc in includes:
        filefound = inc.attrib['schemaLocation']
        files.append(filefound)
        search4Includes(files)


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

            else:
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
        elif child.tag in [NS+'simpleType', NS+'complexType']:
            print('#Skipping ' + child.tag + ' - already processed via searchIncludes.')
            continue
        else:
            parsefile(child, newxml, indent+'  ')

###############################

# This contains the namespace of the XSD, not the targetnamespace of the XML specified by the XSD:
NS = '{http://www.w3.org/2001/XMLSchema}'

# All xsd files describing this xml.
# NB: Primary file must come first.
#xsdfiles = ['IE4N10.xsd']
##, 'ctypes.xsd', 'htypes.xsd', 'stypes.xsd']

xsdfiles = [sys.argv[1]]
search4Includes(xsdfiles)
rootelementname = xsdfiles[0].split('.', 2)[0]
print('Includes: ' + ', '.join(xsdfiles))

showrestrictions = False

# Parse the xsd files, and store their respective roots
# under the filename.
xsdroots = {}
for file in xsdfiles:
    xsdroots[file] = etree.parse(file).getroot()

mainroot = xsdroots[xsdfiles[0]]
if mainroot.tag == NS+'schema' and 'targetNamespace' in mainroot.attrib:
    tns = mainroot.attrib['targetNamespace']
    print('TNS=' + tns)

etree.register_namespace('', tns)

newtree = etree.ElementTree()
newxml = etree.Element(None)
newtree._setroot(newxml)
parsefile(mainroot, newxml)

#newtree.getroot().attrib['xmlns'] = tns
# NB: Default namespace is NOT set, despite various attempts...
#
xmlfilename = rootelementname + '.v2.' + datetime.datetime.now().strftime("%Y-%m-%d") + '.xml'
newtree.write(xmlfilename, encoding='utf-8', xml_declaration=True)
#newtree.write(xmlfilename, encoding="utf-8", xml_declaration=True, default_namespace=tns)


