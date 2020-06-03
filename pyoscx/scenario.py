import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


from .helpers import printToFile
from .utils import FileHeader, ParameterDeclarations
from .enumerations import XMLNS, XSI


class Scenario():
    """ The Scenario class collects all parts of OpenScenario and creates a .xml file

        Attributes
        ----------
            header (FileHeader): the header of the scenario file

            parameters (ParameterDeclarations): the parameters to be used in the scenario

            entities (Entities): the entities in the scenario

            storyboard (StoryBoard): the storyboard of the scenario

            roadnetwork (RoadNetwork): the roadnetwork of the scenario

            catalog (Catalog): the catalogs used in the scenario
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            write_xml(filename)
                write a open scenario xml

    """
    _XMLNS = XMLNS
    _XSI = XSI
    def __init__(self,name,author,parameters,entities,storyboard,roadnetwork,catalog):
        """ Initalizes the Scenario class, and creates the header.

        Parameters
        ----------
            name (str): name of the scenario

            author (str): the author fo the scenario

            parameters (ParameterDeclarations): the parameters to be used in the scenario

            entities (Entities): the entities in the scenario

            storyboard (StoryBoard): the storyboard of the scenario

            roadnetwork (RoadNetwork): the roadnetwork of the scenario

            catalog (Catalog): the catalogs used in the scenario
        """
        self.entities = entities
        self.storyboard = storyboard
        self.roadnetwork = roadnetwork
        self.catalog = catalog 
        self.parameters = parameters
        self.header = FileHeader(name,author)

    def get_element(self):
        """ returns the elementTree of the Scenario

        """
        element = ET.Element('OpenSCENARIO',attrib={'xmlns:xsi':self._XMLNS,'xsi:noNamespaceShemaLocation':self._XSI})
        element.append(self.header.get_element())
        element.append(self.parameters.get_element())
        element.append(self.catalog.get_element())
        element.append(self.roadnetwork.get_element())
        element.append(self.entities.get_element())
        element.append(self.storyboard.get_element())

        return element

    def write_xml(self,filename,prettyprint = True):
        """ writeXml writes the open scenario xml file

        Parameters
        ----------
            filename (str): path and filename of the wanted xml file

            prettyprint (bool): pretty print or ugly print?
                Default: True

        """
        printToFile(self.get_element(),filename,prettyprint)
        



class RoadNetwork():
    """ The RoadNetwork class creates the RoadNetwork of the openScenario
        
        Parameters
        ----------
            roadfile (str): path to the opendrive file

            scenegraph (str): path to the opensceengraph file (optional)

        Attributes
        ----------
            road_file: path to the opendrive file

            scene: path to the opensceengraph file 
            
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class



    """
    def __init__(self,roadfile,scenegraph=None):
        """ Initalizes the RoadNetwork

        Parameters
        ----------
            roadfile (str): path to the opendrive file

            scenegraph (str): path to the opensceengraph file (optional)

        """
        self.road_file = roadfile
        self.scene = scenegraph


    def get_element(self):
        """ returns the elementTree of the RoadNetwork

        """
        roadnetwork = ET.Element('RoadNetwork')
        ET.SubElement(roadnetwork,'LogicFile',{'filepath': self.road_file})
        if self.scene:
            ET.SubElement(roadnetwork,'SceneGraphFile',{'filepath':self.scene})
        return roadnetwork
    