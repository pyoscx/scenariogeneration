import xml.etree.ElementTree as ET

from .utils import EntityRef, ObjectType

class Entities():
    """ The Entities class creates the entities part of OpenScenario
        
        Attributes
        ----------
            scenario_objects (list of ScenarioObject): ScenarioObject type entities in the scenario

            entities (list of Entity): Entity type of entities in the scenario


        Methods
        -------
            add_scenario_object(scenario_object)
                adds a ScenarioObject to the scenario

            add_entity(entity)
                adds an Entity to the scenario

            get_element()
                Returns the full ElementTree of the class


    """
    def __init__(self):
        """ initalizes the Entities class

        """
        self.scenario_objects = []
        self.entities = []


    def add_scenario_object(self,scenario_object):
        """ adds a ScenarioObject to the scenario
        
        Parameters
        ----------
            scenario_object (ScenarioObject): ScenarioObject to add to the scenario

        """

        self.scenario_objects.append(scenario_object)
    
    def add_entity(self,entity):
        """ adds an Entity to the scenario
        
        Parameters
        ----------
            entity (Entity): Entity to add to the scenario

        """
        self.entities.append(entity)

    def get_element(self):
        """ returns the elementTree of the Entities

        """
        element = ET.Element('Entities')
        for i in self.scenario_objects:
            element.append(i.get_element())

        for i in self.entities:
            element.append(i.get_element())

        

        return element

class ScenarioObject():
    """ The ScenarioObject creates a scenario object of OpenScenario
        
        Parameters
        ----------
            name (str): name of the object

        Attributes
        ----------
            name (str): name of the object

            catalog_reference (tuple: (catalog,name)): the vehicle catalog reference

            object_controller (tuple: (catalog,name)): the controller catalot reference 

        Methods
        -------
            set_object_controller(catalog,name)
                sets the controller of the ScenarioObject

            set_catalog_reference(catalog,name)
                sets the vehicle reference to the ScenarioObject

            get_element()
                Returns the full ElementTree of the class


    """

    ###TODO: add so parameters can be added aswell, not just catalogs

    def __init__(self,name):
        """ initalizes the ScenarioObject

        Parameters
        ----------
            name (str): name of the object

        """
        self.name = name
        self.catalog_reference = None
        self.object_controller = None

    def set_object_controller(self,catalog,name):
        """ sets the controller of the ScenarioObject
        
        Parameters
        ----------
            catalog (str): the controller catalog 
            
            name (str): name of the controller

        """
        self.object_controller = (catalog,name)


    def set_catalog_reference(self,catalog,name):
        """ sets the vehicle catalog reference of the ScenarioObject
        
        Parameters
        ----------
            catalog (str): the vehicle catalog 
            
            name (str): name of the vehicle

        """

        self.catalog_reference = (catalog,name)


    def get_element(self):
        """ returns the elementTree of the ScenarioObject

        """
        obj = ET.Element('ScenarioObject', attrib={'name':self.name})
        
        ET.SubElement(obj,'CatalogReference',attrib=self._getCatalogReference(self.catalog_reference))

        controller = ET.SubElement(obj,'ObjectController')
        ET.SubElement(controller,'CatalaogReference',attrib=self._getCatalogReference(self.object_controller))
        return obj

    
    def _getCatalogReference(self,inp_tuple):
        return {'catalogName':inp_tuple[0],'entryName':inp_tuple[1]}

class Entity():
    """ The Entity class creates an Entity of OpenScenario
        Can either use a object_type or entityref (not both)
        
        Parameters
        ----------
            name (str): name of the Entity

            optionals:
                object_type (str): the object_type to be used

                entityref (str): reference to an entity

        Attributes
        ----------
            name (str): name of the Entity

            object_type (str): the object_type to be used

            entityref (str): reference to an entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name,object_type=None,entityref=None):
        """ Initalizes the Entity

        Parameters
        ----------
            name (str): name of the Entity

            optionals (only use one):
                object_type (str): the object_type to be used

                entityref (str): reference to an entity

        """
        self.name = name
        if (object_type !=None) and (entityref != None):
            raise KeyError('only one of objecttype or entityref are alowed')

        self.object_type = ObjectType(object_type)
        self.entity = EntityRef(self.entityref)
        
    def get_attributes(self):
        """ returns the atributes of the Entity as a dict

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Entity

        """
        element = ET.Element('EntitySelection')
        members = ET.SubElement(element,'Members',attrib=self.get_attributes())
        if self.entity:
            members.append(self.entity.get_element())
        if self.object_type:
            ET.SubElement(members,'ByType',self.object_type.get_attributes())