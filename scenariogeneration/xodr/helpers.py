import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


import os

def enum2str(enum):
    """ helper to create strings from enums that should contain space but have to have _

        Parameters
        ----------
            enum (Enum): a enum of pyodrx

        Returns
        -------
            enumstr (str): the enum as a string replacing _ with ' '

    """
    return enum.name.replace('_',' ')


def printToFile(element,filename,prettyprint=True):
    """ prints the element to a xml file

        Parameters
        ----------
            element (Element): element to print

            filename (str): file to save to

            prettyprint (bool): pretty or "ugly" print

    """
    if prettyprint:    
        rough = ET.tostring(element,'utf-8').replace(b'\n',b'').replace(b'\t',b'')
        reparsed = mini.parseString(rough)
        towrite = reparsed.toprettyxml(indent="    ")
        with open(filename,'w') as file_handle:
            file_handle.write(towrite)
    else:
        tree = ET.ElementTree(element)
        with open(filename,"wb") as file_handle:
            tree.write(file_handle)