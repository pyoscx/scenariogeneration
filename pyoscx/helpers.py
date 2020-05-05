import xml.etree.ElementTree as ET
import xml.dom.minidom as mini

def prettyprint(element):
    rough = ET.tostring(element,'utf-8')
    reparsed = mini.parseString(rough)
    print(reparsed.toprettyxml(indent="\t"))