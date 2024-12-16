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

def create_heading(name, author, date, place, type_):
    tei = ET.Element('TEI')
    tei.attrib['xmlns'] = 'http://www.tei-c.org/ns/1.0'

    teiHeader = ET.SubElement(tei, 'teiHeader')
    fileDesc = ET.SubElement(teiHeader, 'fileDesc')
    titleStmt = ET.SubElement(fileDesc, 'titleStmt')
    title = ET.SubElement(titleStmt, 'title')
    title.text = f'{name}'

    author_ = ET.SubElement(titleStmt, 'author')
    author_.text = f'{author}'

    publicationStmt = ET.SubElement(fileDesc, 'publicationStmt')
    date_ = ET.SubElement(publicationStmt, 'date')
    date_.text = f'{date}'

    place_ = ET.SubElement(publicationStmt, 'pubPlace')
    place_.text = f'{place}'

    type__= ET.SubElement(fileDesc, 'type')
    type__.text = f'{type_}'


    return tei

def create_page(tei, img, text):
    pb = ET.SubElement(tei, 'pb')
    pb.attrib['facs'] = img

    div = ET.SubElement(tei, 'div')
    div.attrib['type'] = 'page'

    for line in text.split('\n'):
        p = ET.SubElement(div, 'p')
        p.text = line

    return tei

def generate_xml(img_path: [], text:[[str]], title,
                 author, date, place, type_):
    header = create_heading(title, author, date, place, type_)
    tei = None
    for i in range(len(img_path)):
        tei = create_page(header, img_path[i], text[i])

    tree = ET.ElementTree(tei)
    ET.indent(tei, space="   ")
    #return the string representation of the xml
    return ET.tostring(tei, encoding='utf-8').decode('utf-8')

