import xml.etree.ElementTree as ET
import xml.dom.minidom as mini



def prettyprint(element):
    """ prints the element to the commandline

        Parameters
        ----------
            element (Element): element to print

    """
    rough = ET.tostring(element,'utf-8')
    reparsed = mini.parseString(rough)
    print(reparsed.toprettyxml(indent="\t"))