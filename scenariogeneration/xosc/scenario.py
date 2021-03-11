""" the scenario module contains the main class for generating OpenSCENARIO files aswell as the roadnetwork 

"""

import xml.etree.ElementTree as ET
import xml.dom.minidom as mini


from .helpers import printToFile
from .utils import FileHeader, ParameterDeclarations, Catalog, TrafficSignalController
from .enumerations import XMLNS, XSI
from .entities import Entities
from .storyboard import StoryBoard

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
        if not isinstance(entities,Entities):
            raise TypeError('entities input is not of type Entities')
        if not isinstance(storyboard,StoryBoard):
            raise TypeError('storyboard input is not of type StoryBoard')
        if not isinstance(roadnetwork,RoadNetwork):
            raise TypeError('roadnetwork input is not of type RoadNetwork')
        if not isinstance(catalog,Catalog):
            raise TypeError('catalog input is not of type StorCatalogyBoard')
        if not isinstance(parameters,ParameterDeclarations):
            raise TypeError('parameters input is not of type ParameterDeclarations')

        self.entities = entities
        self.storyboard = storyboard
        self.roadnetwork = roadnetwork
        self.catalog = catalog 
        self.parameters = parameters
        self.header = FileHeader(name,author)

    def get_element(self):
        """ returns the elementTree of the Scenario

        """
        element = ET.Element('OpenSCENARIO',attrib={'xmlns:xsi':self._XMLNS,'xsi:noNamespaceSchemaLocation':self._XSI})
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
            road_file (str): path to the opendrive file

            scene (str): path to the opensceengraph file 

            traffic_signals (list of TrafficSignalController): all traffic signals in the roadnetwork
            
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
        self.traffic_signals = []

    def add_traffic_signal_controller(self,traffic_signal_controller):
        """ adds a TrafficSignalController to the RoadNetwork

            Parameters
            ----------
                traffic_signal_controller (TrafficSignalController): the traffic signal controller to add

        """
        if not isinstance(traffic_signal_controller,TrafficSignalController):
            raise TypeError('traffic_signal_controller input is not of type TrafficSignalController')
        self.traffic_signals.append(traffic_signal_controller)

    def get_element(self):
        """ returns the elementTree of the RoadNetwork

        """
        roadnetwork = ET.Element('RoadNetwork')
        ET.SubElement(roadnetwork,'LogicFile',{'filepath': self.road_file})
        if self.scene:
            ET.SubElement(roadnetwork,'SceneGraphFile',{'filepath':self.scene})
        if self.traffic_signals:
            trafsign_element = ET.SubElement(roadnetwork,'TrafficSignals')
            for ts in self.traffic_signals:
                trafsign_element.append(ts.get_element())
        return roadnetwork
    