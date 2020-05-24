import os
import xml.etree.ElementTree as ET
from .utils import FileHeader
from .enumerations import XSI,XMLNS
from .helpers import printToFile

class CatalogFile():
    """ The CatalogFile class handles any catalogs in open scenario, such as writing, and updating them
        
        Parameters
        ----------
            prettyprint (boolean): if the final file should have prettyprint or not
                Default: True

        Attributes
        ----------
            prettyprint: if the final file should have prettyprint or not

            catalog_element (Element): the element that is worked with

            filename (str): path to the file to be written to

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_catalog(catalogname, path)
                Adds a new catalog 
    """

    def __init__(self,prettyprint = True):
        """ initalize the CatalogFile class

            Parameters
            ----------
                prettyprint (boolean): if the final file should have prettyprint or not
                    Default: True
        """
        self.prettyprint = prettyprint
        self.catalog_element = None
        self.filename = ''

    def add_to_catalog(self,obj):
        """ add_to_catalog adds an element to the catalog
            
            Parameters
            ----------
                obj (*pyoscx): any pyoscx object (should be matching with the catalog)
        
        """
        if self.catalog_element == None:
            OSError('No file has been created or opened')
        catalogs = self.catalog_element.find('Catalog')
        catalogs.append(obj.get_element())

    def open_catalog(self,filename):
        """ open_catalog reads an existing catalog file
            
            Parameters
            ----------
                filename (str): path to the catalog file

        """
        self.filename = filename
        tree = ET.parse(self.filename)
        self.catalog_element = tree.getroot()

    def create_catalog(self,filename,catalogtype,description,author):
        """ create_catalog_element creates an empty catalog of a desiered type, 
            
            Parameters
            ----------
                filename (str): path of the new catalog file

                catalogtype (str): name of the catalog

                description (str): description of the catalog

                author (str): author of the catalog
        
        """
        self.filename = filename
        self.catalog_element = self.create_catalog_element(catalogtype,description,author)


    def create_catalog_element(self,catalogtype,description,author):
        """ create_catalog_element creates an empty catalog of a desiered type, 
            
            Parameters
            ----------
                catalogtype (str): name of the catalog

                description (str): description of the catalog

                author (str): author of the catalog
        
        """
        element = ET.Element('OpenSCENARIO',attrib={'xmlns:xsi':XMLNS,'xsi:noNamespaceShemaLocation':'../../'+XSI})
        header = FileHeader(description,author)
        element.append(header.get_element())
        ET.SubElement(element,'Catalog',attrib={'name':catalogtype})

        return element

    def dump(self):
        """ writes the new/updated catalog file

        """
        printToFile(self.catalog_element,self.filename,self.prettyprint)

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

class CatalogReference():
    """ CatalogReference creates an CatalogReference element of openscenario
        
        Parameters
        ----------
            catalogname (str): name of the catalog

            entryname (str): name of the entry in the catalog            

        Attributes
        ----------
            catalogname (str): name of the catalog

            entryname (str): name of the entry in the catalog 

            parameter (Parameter) ???

        Methods
        -------
            add_parameter_assignment(parameter,value)
                Assigns a parameter with a value

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,catalogname,entryname):
        """ initalize the CatalogReference

            Parameters
            ----------
                catalogname (str): name of the catalog

                entryname (str): name of the entry in the catalog    
                
        """
        self.catalogname = catalogname
        self.entryname = entryname

    def get_attributes(self):
        """ returns the attributes of the CatalogReference as a dict

        """
        return {'catalogName':self.catalogname,'entryName':self.entryname}

    def get_element(self):
        """ returns the elementTree of the CatalogReference

        """
        return ET.Element('CatalogReference',attrib=self.get_attributes())
    