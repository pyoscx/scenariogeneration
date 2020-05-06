import xml.etree.ElementTree as ET
import xml.dom.minidom as mini

import datetime as dt
from .helpers import printToFile

class Scenario():
    _XMLNS = 'http://www.w3.org/2001/XMLSchema-instance'
    _XSI = 'OpenSccenario.xsd'
    """ The Scenario class collects all parts of OpenScenario and creates a .xml file
        
        Parameters
        ----------
            name (str): name of the scenario

            author (str): the author fo the scenario

            parameters (ParameterDeclarations): the parameters to be used in the scenario

            entities (Entities): the entities in the scenario

            storyboard (StoryBoard): the storyboard of the scenario

            roadnetwork (RoadNetwork): the roadnetwork of the scenario

            catalog (Catalog): the catalogs used in the scenario

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
        element = ET.Element('Openscenario',attrib={'xmlns:xsi':self._XMLNS,'xsi:noNamespaceShemaLocation':self._XSI})
        element.append(self.header.get_element()),
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
        

class FileHeader():
    """ FileHeader creates the header of the OpenScenario file
        
        Parameters
        ----------
            name (str): name of the scenario 

            author (str): the author of the scenario

        Attributes
        ----------
            name (str): name of the scenario 

            author (str): the author of the scenario

        Methods
        -------
            get_element()
                Returns the full ElementTree of FileHeader

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

    """
    def __init__(self,name,author):
        self.name = name
        self.author = author
        

    def get_attributes(self):
        """ returns the atributes as a dict of the FileHeader

        """
        return {'decription':self.name,'author':self.author,'revMajor':'1','revMinor':'0','date':str(dt.datetime.now())}

    def get_element(self):
        """ returns the elementTree of the FileHeader

        """
        element = ET.Element('FileHeader',attrib=self.get_attributes())

        return element



class Catalog():
    """ The Catalog class creates the CatalogLocation of the OpenScenario input
        
        Parameters
        ----------

        Attributes
        ----------
            catalogs: dict of catalogs to add, and their path
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_catalog(catalogname, path)
                Adds a new catalog 
    """
    _CATALOGS = [\
        'VehicleCatalog',
        'ControllerCatalog',
        'PedestrianCatalog',
        'MiscObjectCatalog',
        'EnvironmentCatalog',
        'ManeuverCatalog',
        'TrajectoryCatalog',
        'RouteCatalog']

    def __init__(self):
        """ initalize the Catalog class

        """
        self.catalogs = {}

    def add_catalog(self,catalogname,path):
        """ add new catalog to be used

        Parameters
        ----------
            catalogname (str): name of the catalog

            path (str): path to the catalog
        
        """


        if catalogname not in self._CATALOGS:
            raise ValueError('Not a correct catalog, approved catalogs are:' ''.join(self._CATALOGS))
        
        self.catalogs[catalogname] = path


    def get_element(self):
        """ returns the elementTree of the Catalog

        """
        
        catloc = ET.Element('CatalogLocations')
        
        for i in self.catalogs:
            tmpel = ET.SubElement(catloc,i)
            ET.SubElement(tmpel,'Directory',{'path': self.catalogs[i]})
        return catloc

class ParameterDeclarations():
    """ The ParameterDeclarations class creates the ParameterDeclaration of OpenScenario
                    
        Attributes
        ----------
            parameters: list of Parameter objects

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_parameter(Parameter)
                adds a Parameter to the ParameterDeclarations

    """
    def __init__(self):
        """ initalizes the ParameterDeclarations

        """
        self.parameters = []

    def add_parameter(self,parameter):
        """ add_parameter adds a Parameter to the ParameterDeclarations

        Parameters
        ----------
            parameter (Parameter): a new parameter


        """
        self.parameters.append(parameter)
    
    def get_element(self):
        """ returns the elementTree of the ParameterDeclarations

        """
        element = ET.Element('ParameterDeclarations')
        for p in self.parameters:
            element.append(p.get_element())
        return element

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
    