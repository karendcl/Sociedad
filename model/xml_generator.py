import xml.etree.ElementTree as ET


def read_xml(path):
    with open(path, 'r') as f:
        return f.read()

def decode_xml(path):
    tree = ET.parse(path)
    root = tree.getroot()

    #get filename from root
    filename = root.attrib['filename']

    lines = []

    for child in root:
        for subchild in child:
            lines.append(subchild.attrib['text'])

    return filename, lines

def transform_tei_format(img_name, lines, title_):
    tei = ET.Element('TEI')
    tei.attrib['xmlns'] = 'http://www.tei-c.org/ns/1.0'

    pb = ET.SubElement(tei, 'pb')
    pb.attrib['facs'] = img_name

    teiHeader = ET.SubElement(tei, 'teiHeader')
    fileDesc = ET.SubElement(teiHeader, 'fileDesc')
    titleStmt = ET.SubElement(fileDesc, 'titleStmt')
    title = ET.SubElement(titleStmt, 'title')
    title.text = f'{title_}'


    text = ET.SubElement(tei, 'text')
    body = ET.SubElement(text, 'body')
    div = ET.SubElement(body, 'div')
    div.attrib['type'] = 'page'

    for line in lines:
        p = ET.SubElement(div, 'p')
        p.text = line

    return tei

def save_tei(tei, path):
    tree = ET.ElementTree(tei)
    ET.indent(tei, space="   ")
    tree.write(path)

def generate_xml(img_path, text:[str], title):
    tei = transform_tei_format(img_path, text, title)
    tree = ET.ElementTree(tei)
    ET.indent(tei, space="   ")
    #return the string representation of the xml
    return ET.tostring(tei, encoding='utf-8').decode('utf-8')

