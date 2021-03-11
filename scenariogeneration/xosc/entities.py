""" the entities module contains the classes related to the Entities entries of OpenSCENARIO.

"""
import xml.etree.ElementTree as ET
from .utils import Controller, Dimensions, Center, BoundingBox, Properties, Parameter
from .utils import EntityRef
from .scenario import ParameterDeclarations
from .enumerations import VehicleCategory, PedestrianCategory, MiscObjectCategory, ObjectType
from .utils import DynamicsConstrains, CatalogFile, CatalogReference


class Entities():
    """ The Entities class creates the entities part of OpenScenario
        
        Attributes
        ----------
            scenario_objects (list of ScenarioObject): ScenarioObject type entities in the scenario

            entities (list of Entity): Entity type of entities in the scenario


        Methods
        -------
            add_scenario_object(entityobject,controller)
                adds a ScenarioObject to the scenario

            add_entity_bytype(name,entity_type)
                adds an Entity by the type of entity

            add_entity_byref(name,reference)
                adds an Entity by a reference name

            get_element()
                Returns the full ElementTree of the class


    """
    def __init__(self):
        """ initalizes the Entities class

        """
        self.scenario_objects = []
        self.entities = []


    def add_scenario_object(self, name, entityobject, controller=None):
        """ adds a ScenarioObject to the scenario
        
            Parameters
            ----------
                name (str): name of the scenario object

                entityobject (CatalogReference, Vehicle, Pedestrian, or MiscObject): object description

                controller (CatalogReference, or Controller): controller for the object
                    Default (None)

        """

        self.scenario_objects.append(ScenarioObject(name,entityobject,controller))
    
    def add_entity_bytype(self,name,object_type):
        """ adds an Entity to the scenario
        
            Parameters
            ----------
                name (str): name of the entity

                object_type (ObjectType): type of entity
            
        """
        self.entities.append(Entity(name,object_type=object_type))

    def add_entity_byref(self,name,entity):
        """ adds an Entity to the scenario
        
            Parameters
            ----------
                name (str): name of the entity

                entity (str): type of entity
            
        """

        self.entities.append(Entity(name,entityref=entity))


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

            entityobject (CatalogReference, Vehicle, Pedestrian, or MiscObject): object description

            controller (CatalogReference, or Controller): controller for the object

        Attributes
        ----------
            name (str): name of the object

            entityobject (CatalogReference, Vehicle, Pedestrian, or MiscObject): object description

            controller (CatalogReference, or Controller): controller for the object

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class
            
            get_attributes()
                returns the attributes of the class
    """ 
    def __init__(self ,name ,entityobject ,controller = None):
        """ initalizes the ScenarioObject

            Parameters
            ----------
                name (str): name of the object

                entityobject (CatalogReference, Vehicle, Pedestrian, or MiscObject): object description

                controller (CatalogReference, or Controller): controller for the object
                    Default: None

        """
        self.name = name
        if not (isinstance(entityobject,CatalogReference) or isinstance(entityobject,Vehicle) or isinstance(entityobject,Pedestrian) or isinstance(entityobject,MiscObject)):
            raise TypeError('entityobject is not of type CatalogReference, Vehicle, Pedestrian, nor MiscObject')
        
        if controller is not None and not (isinstance(controller,CatalogReference) or isinstance(controller,Controller)):
            raise TypeError('controller input is not of type CatalogReference or Controller')
        self.entityobject = entityobject
        self.controller = controller

    def get_attributes(self):
        """ returns the attributes of the Entity as a dict

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Entity

        """
        element = ET.Element('ScenarioObject',attrib=self.get_attributes())
        
        element.append(self.entityobject.get_element())
        if self.controller:
            objcont = ET.SubElement(element,'ObjectController')
            objcont.append(self.controller.get_element())
        
        return element

class Entity():
    """ The Entity class creates an Entity of OpenScenario
        Can either use a object_type or entityref (not both)
        
        Parameters
        ----------
            name (str): name of the Entity

            optionals:
                object_type (ObjectType): the object_type to be used

                entityref (str): reference to an entity

        Attributes
        ----------
            name (str): name of the Entity

            object_type (ObjectType): the object_type to be used

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
                object_type (ObjectType): the object_type to be used

                entityref (str): reference to an entity

        """
        self.name = name
        if (object_type !=None) and (entityref != None):
            raise KeyError('only one of objecttype or entityref are alowed')
        if (object_type ==None) and (entityref == None):
            raise KeyError('either objecttype or entityref is requiered')
        if entityref:
            self.entity = EntityRef(entityref)
            self.object_type = None
        else:
            if object_type not in ObjectType:
                ValueError('object_type input not a valid ObjectType')
            self.object_type = object_type
            self.entity = None
        
    def get_attributes(self):
        """ returns the attributes of the Entity as a dict

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Entity

        """
        element = ET.Element('EntitySelection',attrib=self.get_attributes())
        members = ET.SubElement(element,'Members')
        if self.entity:
            members.append(self.entity.get_element())
        if self.object_type:
            ET.SubElement(members,'ByType',attrib={'value':self.object_type.name})
        return element

class Pedestrian():
    """ the Pedestrian class creates a pedestrian type entity of openscenario

        Parameters
        ----------
            name (str): name of the type (req for catalog)

            model (str): definition model of the pedestrian

            mass (float): mass of the pedestrian

            boundingbox (BoundingBox): the bounding box of the pedestrian

            category (PedestrianCategory): type of of pedestrian 
                

        Attributes
        ----------
            name (str): name of the pedestrian

            model (str): definition model of the pedestrian

            mass (float): mass of the pedestrian

            category (PedestrianCategory): type of pedestrian

            boundingbox (BoundingBox): the bounding box of the pedestrian

            parameters (ParameterDeclaration): Parameter declarations of the pedestrian

            properties (Properties): additional properties of the pedestrian

        Methods
        -------
            add_parameter(parameter)
                adds a parameter declaration to the pedestrian

            add_property(name, value)
                adds a single property to the pedestrian

            add_property_file(filename)
                adds a property file to the pedestrian

            append_to_catalog(filename)
                adds the vehicle to an existing pedestrian

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the pedestrian

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name, model, mass, category, boundingbox):
        """ initalzie the Pedestrian Class

        Parameters
        ----------
            name (str): name of the type (req for catalog)

            model (str): definition model of the pedestrian

            mass (float): mass of the pedestrian

            category (PedestrianCategory): type of of pedestrian 

            boundingbox (BoundingBox): the bounding box of the pedestrian
        
        """
        self.name = name
        self.model = model
        self.mass = mass
        if category not in PedestrianCategory:
            ValueError(str(category) + ' is not a valid pedestrian type')    
        if not isinstance(boundingbox,BoundingBox):
            raise TypeError('boundingbox input is not of type BoundingBox')

        self.category = category
        self.boundingbox = boundingbox
        self.parameters = ParameterDeclarations()
        self.properties = Properties()

        
    
    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the Pedestrian to it
            
            Parameters
            ----------
                filename (str): path of the new catalog file

                catalogtype (str): name of the catalog

                description (str): description of the catalog

                author (str): author of the catalog
        
        """
        cf = CatalogFile()
        cf.create_catalog(filename,catalogtype,description,author)
        cf.add_to_catalog(self)
        cf.dump()
        
    def append_to_catalog(self,filename):
        """ adds the Pedestrian to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()
        
    def add_parameter(self,parameter):
        """ adds a parameter declaration to the pedestrian

            Parameters
            ----------
                parameter (Parameter): A new parameter declaration for the pedestrian

        """
        if not isinstance(parameter,Parameter):
            raise TypeError('parameter input is not of type Parameter')
        self.parameters.add_parameter(parameter)

    def add_property(self,name, value):
        """ adds a single property to the pedestrian

            Parameters
            ----------
                name (str): name of the property

                value (str): value of the property

        """
        self.properties.add_property(name,value)

    def add_property_file(self,filename):
        """ adds a property file to the pedestrian

            Parameters
            ----------
                filename (str): filename of a property file

        """
        self.properties.add_file(filename)

    def get_attributes(self):
        """ returns the attributes as a dict of the pedestrian

        """
        return {'name':str(self.name),'pedestrianCategory':self.category.name,'model':self.model,'mass':str(self.mass)}

    def get_element(self):
        """ returns the elementTree of the pedestrian

        """
        element = ET.Element('Pedestrian',attrib=self.get_attributes())
        element.append(self.parameters.get_element())
        element.append(self.boundingbox.get_element())
        element.append(self.properties.get_element())
        
        return element

class MiscObject():
    """ the MiscObject Class creates a MiscObject for openscenario

        Parameters
        ----------
            name (str): name of the MiscObject

            mass (float): mass of the object

            category (MiscObjectCategory): the category of the misc object

            boundingbox (BoundingBox): the bounding box of the MiscObject               

        Attributes
        ----------
            name (str): name of the object

            mass (float): mass of the object

            misc_type (MiscObjectCategory): type of misc object

            boundingbox (BoundingBox): the bounding box of the MiscObject

            parameters (ParameterDeclaration): Parameter declarations of the MiscObject

            properties (Properties): additional properties of the MiscObject

        Methods
        -------
            add_parameter(parameter)
                adds a parameter declaration to the MiscObject

            add_property(name, value)
                adds a single property to the MiscObject

            add_property_file(filename)
                adds a property file to the MiscObject

            append_to_catalog(filename)
                adds the MiscObject to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the MiscObject

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name, mass, category, boundingbox):
        """ initalzie the MiscObject Class

        Parameters
        ----------
            name (str): name of the MiscObject

            mass (float): mass of the object

            category (MiscObjectCategory): the category of the misc object

            boundingbox (BoundingBox): the bounding box of the MiscObject       
        
        """
        self.name = name
        self.mass = mass
        if category not in MiscObjectCategory:
            raise TypeError(str(category) + ' is not a valid MiscObject type')    
        self.category = category
        if not isinstance(boundingbox,BoundingBox):
            raise TypeError('boundingbox input is not of type BoundingBox')
        self.boundingbox = boundingbox
        self.parameters = ParameterDeclarations()
        self.properties = Properties()

       
    
    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the MiscObject to it
            
            Parameters
            ----------
                filename (str): path of the new catalog file

                catalogtype (str): name of the catalog

                description (str): description of the catalog

                author (str): author of the catalog
        
        """
        cf = CatalogFile()
        cf.create_catalog(filename,catalogtype,description,author)
        cf.add_to_catalog(self)
        cf.dump()
        
    def append_to_catalog(self,filename):
        """ adds the MiscObject to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()

    def add_parameter(self,parameter):
        """ adds a parameter declaration to the MiscObject

            Parameters
            ----------
                parameter (Parameter): A new parameter declaration for the MiscObject

        """
        if not isinstance(parameter,Parameter):
            raise TypeError('parameter input is not of type Parameter')
        self.parameters.add_parameter(parameter)

    def add_property(self,name, value):
        """ adds a single property to the MiscObject

            Parameters
            ----------
                name (str): name of the property

                value (str): value of the property

        """
        self.properties.add_property(name,value)

    def add_property_file(self,filename):
        """ adds a property file to the MiscObject

            Parameters
            ----------
                filename (str): filename of a property file

        """
        self.properties.add_file(filename)

    def get_attributes(self):
        """ returns the attributes as a dict of the MiscObject

        """
        return {'name':str(self.name),'MiscObjectCategory':str(self.category),'mass':str(self.mass)}

    def get_element(self):
        """ returns the elementTree of the MiscObject

        """
        element = ET.Element('MiscObject',attrib=self.get_attributes())
        element.append(self.parameters.get_element())
        element.append(self.boundingbox.get_element())
        element.append(self.properties.get_element())
        
        return element

class Vehicle():
    """ the Vehicle Class creates a Vehicle for openscenario

        Parameters
        ----------
            name (str): name of the vehicle

            vehicle_type (VehicleCategory): type of vehicle

            boundingbox (BoundingBox): the bounding box of the vehicle

            frontaxle (Axle): the front axle properties of the vehicle

            rearaxle (Axle): the back axle properties of the vehicle

            max_speed (float): the maximum speed of the vehicle

            max_acceleration (float): the maximum acceleration of the vehicle

            max_deceleration (float): the maximum deceleration of the vehicle
                

        Attributes
        ----------
            name (str): name of the vehicle

            vehicle_type (VehicleCategory): type of vehicle

            boundingbox (BoundingBox): the bounding box of the vehicle

            axles (Axles): an Axles object

            dynamics (DynamicsConstraints): the allowed dynamics of the vehicle

            parameters (ParameterDeclaration): Parameter declarations of the vehicle

            properties (Properties): additional properties of the vehicle

        Methods
        -------
            add_axle(axle)
                adds an additional axle to the vehicle

            add_parameter(parameter)
                adds a parameter declaration to the vehicle

            add_property(name, value)
                adds a single property to the vehicle

            add_property_file(filename)
                adds a property file to the vehicle

            append_to_catalog(filename)
                adds the vehicle to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the vehicle

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,name, vehicle_type, boundingbox, frontaxle, rearaxle, max_speed, max_acceleration, max_deceleration):
        """ initalzie the Vehicle Class

            Parameters
            ----------
                name (str): name of the vehicle

                vehicle_type (VehicleCategory): type of vehicle

                boundingbox (BoundingBox): the bounding box of the vehicle

                frontaxle (Axle): the front axle properties of the vehicle

                rearaxle (Axle): the back axle properties of the vehicle

                max_speed (float): the maximum speed of the vehicle

                max_acceleration (float): the maximum acceleration of the vehicle

                max_deceleration (float): the maximum deceleration of the vehicle
        
        """
        self.name = name
        if vehicle_type not in VehicleCategory:
            raise TypeError(vehicle_type + ' is not a valid vehicle type.')  
        if not isinstance(boundingbox,BoundingBox):
            raise TypeError('boundingbox input is not of type BoundingBox')
        
        self.vehicle_type = vehicle_type
        self.boundingbox = boundingbox

        self.axles = Axles(frontaxle,rearaxle)
        self.dynamics = DynamicsConstrains(max_acceleration,max_deceleration,max_speed)
        self.parameters = ParameterDeclarations()
        self.properties = Properties()

    
    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the vehicle to it
            
            Parameters
            ----------
                filename (str): path of the new catalog file

                catalogtype (str): name of the catalog

                description (str): description of the catalog

                author (str): author of the catalog
        
        """
        cf = CatalogFile()
        cf.create_catalog(filename,catalogtype,description,author)
        cf.add_to_catalog(self)
        cf.dump()
        
    def append_to_catalog(self,filename):
        """ adds the vehicle to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()

    def add_axle(self,axle):
        """ adds an additional axle to the vehicle

            Parameters
            ----------
                axle (Axle): an additional Axle

        """
        
        self.axles.add_axle(axle)


    def add_parameter(self,parameter):
        """ adds a parameter declaration to the vehicle

            Parameters
            ----------
                parameter (Parameter): A new parameter declaration for the vehicle

        """
        if not isinstance(parameter,Parameter):
            raise TypeError('parameter input is not of type Parameter')
        self.parameters.add_parameter(parameter)

    def add_property(self,name, value):
        """ adds a single property to the vehicle

            Parameters
            ----------
                name (str): name of the property

                value (str): value of the property

        """
        self.properties.add_property(name,value)

    def add_property_file(self,filename):
        """ adds a property file to the vehicle

            Parameters
            ----------
                filename (str): filename of a property file

        """
        self.properties.add_file(filename)

    def get_attributes(self):
        """ returns the attributes as a dict of the Center

        """
        return {'name':str(self.name),'vehicleCategory':str(self.vehicle_type.name)}

    def get_element(self):
        """ returns the elementTree of the Center

        """
        element = ET.Element('Vehicle',attrib=self.get_attributes())
        element.append(self.parameters.get_element())
        element.append(self.boundingbox.get_element())
        element.append(self.dynamics.get_element('Performance'))
        element.append(self.axles.get_element())
        element.append(self.properties.get_element())
        
        return element




class Axle():
    """ the Axle describes the axle properties of a vehicle

        Parameters
        ----------
            maxsteer (double): max steering angle

            wheeldia (double): diameter of wheel

            track_width (double): distance between wheelcenter

            xpos (double): x position of axle relative to car reference

            zpos (double): z position of axle relative to car reference

        Attributes
        ----------
            maxsteer (double): max steering angle

            wheeldia (double): diameter of wheel

            track_width (double): distance between wheelcenter

            xpos (double): x position of axle relative to car reference

            zpos (double): z position of axle relative to car reference

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns the attributes of the class

            
    """
    def __init__(self,maxsteer,wheeldia,track_width,xpos, zpos):
        """ initalzie the Axle

            Parameters
            ----------
                maxsteer (double): max steering angle

                wheeldia (double): diameter of wheel

                track_width (double): distance between wheelcenter

                xpos (double): x position of axle relative to car reference

                zpos (double): z position of axle relative to car reference
        """
        self.maxsteer = maxsteer
        self.wheeldia = wheeldia
        self.track_width = track_width
        self.xpos = xpos
        self.zpos = zpos

    def get_attributes(self):
        """ returns the attributes of the Axle as a dict

        """
        return {'maxSteering':str(self.maxsteer),'wheelDiameter':str(self.wheeldia),'trackWidth':str(self.track_width),'positionX':str(self.xpos),'positionZ':str(self.zpos)}

    def get_element(self, elementname='AdditionalAxle'):
        """ returns the elementTree of the Axle

        """
        return ET.Element(elementname, attrib=self.get_attributes())
        
class Axles():
    """ the Axles combines the different Axles to one Element

        Parameters
        ----------
            frontaxle (Axle): Axle properties of the front axle

            rearaxle (Axle): Axle properties of the rear axle

        Attributes
        ----------
            frontaxle (Axle): Axle properties of the front axle

            rearaxle (Axle): Axle properties of the rear axle

            additionals (Axle): additional axles if requiered


        Methods
        -------
            add_axle(Axle)
                adds an additional axle to the Axles

            get_element()
                Returns the full ElementTree of the class


    """
    def __init__(self,frontaxle,rearaxle):
        """ initalzie the Axle

            Parameters
            ----------
                frontaxle (Axle): Axle properties of the front axle

                rearaxle (Axle): Axle properties of the rear axle

        """
        if not isinstance(frontaxle,Axle):
            raise TypeError('frontaxle input is not of type Axle')
        if not isinstance(rearaxle,Axle):
            raise TypeError('rearaxle input is not of type Axle')
        self.frontaxle = frontaxle
        self.rearaxle = rearaxle
        self.additionals = []

    def add_axle(self,axle):
        """ adds an additional axle to the Axles

            Parameters
            ----------
                frontaxle (Axle): Axle properties of the front axle

        """
        if not isinstance(axle,Axle):
            raise TypeError('axle input is not of type Axle')
        self.additionals.append(axle)

    def get_element(self):
        """ returns the elementTree of the Axle

        """
        element = ET.Element('Axles')
        element.append(self.frontaxle.get_element(elementname='FrontAxle'))
        element.append(self.rearaxle.get_element(elementname='RearAxle'))
        for ax in self.additionals:
            element.append(ax.get_element())

        return element
