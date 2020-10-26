import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


import os


def run_road(opendrive,esminipath = 'esmini'):
    """ write a scenario and runs it in esminis OpenDriveViewer with some random traffic
        Parameters
        ----------
            opendrive (OpenDrive): the pyodrx road to run

            esminipath (str): the path to esmini 
                Default: pyoscx

    """
    _scenariopath = os.path.join(esminipath,'resources','xodr')
    print(_scenariopath)
    opendrive.write_xml(os.path.join(_scenariopath,'pythonroad.xodr'),True)
    
    if os.name == 'posix':
        os.system(os.path.join('.', esminipath, 'bin','odrviewer') + ' --odr ' + os.path.join(esminipath,'resources','xodr','pythonroad.xodr') + ' --osi_features on --clear-color 0.2,0.2,0.2 --window 50 50 800 400 --density 15' )
    elif os.name == 'nt':
        os.system(os.path.join(esminipath,'bin','odrviewer.exe') + ' --odr ' + os.path.join(esminipath,'resources','xodr','pythonroad.xodr') + ' --osi_features on --clear-color 0.2,0.2,0.2 --window 50 50 800 400 --density 15' )


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

def prettyprint(element):
    """ prints the element to the commandline

        Parameters
        ----------
            element (Element): element to print

    """
    rough = ET.tostring(element,'utf-8')
    reparsed = mini.parseString(rough)
    print(reparsed.toprettyxml(indent="\t"))


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
        towrite = reparsed.toprettyxml(indent="\t")
        with open(filename,"w") as file_handle:
            file_handle.write(towrite)
    else:
        tree = ET.ElementTree(element)
        with open(filename,"wb") as file_handle:
            tree.write(file_handle)