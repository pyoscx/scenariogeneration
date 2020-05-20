
import xml.etree.ElementTree as ET

from .enumerations import CONDITIONEDGE, OBJECTTYPE, PARAMETERTYPE, RULE, REFERENCECONTEXT, DYNAMICSSHAPES, DYNAMICSDIMENSION

from .scenario import ParameterDeclarations
def merge_dicts(*dict_args):
    """ Funciton to merge dicts 
    
    """
    retdict = {}
    for d in dict_args:
        retdict.update(d)

    return retdict


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
    
class ConditionEdge():
    """ ConditionEdge is used to determine how to trigger on a valuechange
        
        Parameters
        ----------
            condition (str): what valuechange to use rising, falling, risingorFalling or none

        Attributes
        ----------
            condition (str): what valuechange to use rising, falling, risingorFalling or none

        Methods
        -------

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,condition):
        """ initalize the ConditionEdge

            Parameters
            ----------
                condition (str): what valuechange to use rising, falling, risingorFalling or none

        """
        if condition not in CONDITIONEDGE:
            raise ValueError('not a valid condition edge')
        self.condition = condition

    def get_attributes(self):
        """ returns the attributes of the ConditionEdge as a dict

        """
        return {'conditionEdge':self.condition}


class EntityRef():
    """ EntityRef creates an EntityRef element of openscenario
        
        Parameters
        ----------
            entity (str): name of the entity

        Attributes
        ----------
            entity (str): name of the entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,entity):
        """ initalize the EntityRef

            Parameters
            ----------
                entity (str): name of the entity
                
        """
        self.entity = entity

    def get_attributes(self):
        """ returns the attributes of the EntityRef as a dict

        """
        return {'entityRef':self.entity}

    def get_element(self):
        """ returns the elementTree of the EntityRef

        """
        return ET.Element('EntityRef',attrib=self.get_attributes())

class ObjectType():
    """ creates an objecttype of openscenario
        
        Parameters
        ----------
            obj_type (str): the typ of object, vehicle, pedestrian or miscellaneous
            
        Attributes
        ----------
            type (str): the typ of object

        Methods
        -------

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,obj_type):
        """ initalize the ObjectType

            Parameters
            ----------
                obj_type (str): the typ of object, vehicle, pedestrian or miscellaneous

        """
        if obj_type not in OBJECTTYPE:
            raise ValueError('not a valid object type')

        self.type = obj_type

    def get_attributes(self):
        """ returns the attributes of the Parameter as a dict

        """
        return {'value':self.type}


class Parameter():
    """ Parameter is a declaration of a ParameterDeclaration for declarations
        
        Parameters
        ----------
            name (str): name of parameter

            parameter_type (str): type of the parameter ('integer', 'double', 'string', 'unsighedInt', 'unsighedShort', 'boolean', 'dateTime')

            value (str): value of the parameter

        Attributes
        ----------
            name (str): name of parameter

            parameter_type (str): type of the parameter

            value (str): value of the parameter

        Methods
        -------
            add_parameter ???

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    
    def __init__(self,name,parameter_type,value):
        """ initalize the Parameter 

            Parameters
            ----------
                name (str): name of parameter

                parameter_type (str): type of the parameter

                value (str): value of the parameter

        """
        self.name = name
        if parameter_type not in PARAMETERTYPE:
            raise ValueError('parameter_type not a valid type.')
        self.parameter_type = parameter_type
        self.value = value

    def get_attributes(self):
        """ returns the attributes of the Parameter as a dict

        """
        return {'name':self.name,'parameterType':self.parameter_type,'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the Parameter

        """
        element = ET.Element('ParameterDeclaration',attrib=self.get_attributes())
        return element

class Rule():
    """ Creates a Rule of a comparison
        
        Parameters
        ----------
            rule: what to apply (greaterThan, lessThan, or equalTo)

            parameter: ???

        Attributes
        ----------
            rule: what to apply (greaterThan, lessThan, or equalTo)

            parameter: ???

        Methods
        -------

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,rule,parameter = None):
        """ initalize the Rule
            Parameters
            ----------
                rule: what to apply (greaterThan, lessThan, or equalTo)

                parameter: ???

        """
        if rule not in RULE:
            raise ValueError(rule + '; is not a valid rule.')
        self.rule = rule
        self.parameter = parameter

    def get_attributes(self):
        """ returns the attributes of the Rule as a dict

        """
        return {'rule':self.rule}


class Orientation():
    """ Orientation describes the angular orientation of an entity
        
        Parameters
        ----------
            h (float): header 

            p (float): pitch

            r (float): roll

            reference (str): absolute or relative

        Attributes
        ----------
            h (float): header 

            p (float): pitch

            r (float): roll

            reference (str): absolute or relative

        Methods
        -------
            is_filled()
                check is any orientations are set

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,h=None,p=None,r=None,reference = None):
        
        self.h = h
        self.p = p
        self.r = r

        if (reference not in REFERENCECONTEXT) and (reference != None):
            raise ValueError(str(reference) + '; is not a valid reference type.')
        self.ref = reference

    def is_filled(self):
        """ is_filled check is any orientations are  set

            Returns: boolean

        """
        if self.h or self.p or self.r or self.ref:
            return True
        else:
            return False
    
    def get_attributes(self):
        """ returns the attributes of the DynamicsConstrains as a dict

        """
        retdict = {}
        if self.h:
            retdict['h'] = str(self.h)

        if self.p:
            retdict['p'] = str(self.p)

        if self.r:
            retdict['r'] = str(self.r)

        if self.ref:
            retdict['type'] = str(self.ref)
        
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element('Orientation',attrib=self.get_attributes())

class TransitionDynamics():
    """ TransitionDynamics is used to define how the dynamics of a change
        
        Parameters
        ----------
            shape (str): shape of the transition

            dimension (str): the dimension of the transition (rate, time or distance)

            value (float): the value of the dynamics (time rate or distance)


        Attributes
        ----------
            shape (str): shape of the transition

            dimension (str): the dimension of the transition (rate, time or distance)

            value (float): the value of the dynamics (time rate or distance)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,shape,dimension,value):
        """
            Parameters
            ----------
                shape (str): shape of the transition

                dimension (str): the dimension of the transition (rate, time or distance)

                value (float): the value of the dynamics (time rate or distance)

        """
        if shape not in DYNAMICSSHAPES:
            raise ValueError(shape + '; is not a valid shape.')
        
        self.shape = shape
        if dimension not in DYNAMICSDIMENSION:
            raise ValueError(dimension + ' is not a valid dynamics dimension')
        self.dimension = dimension
        self.value = value

    def get_attributes(self):
        """ returns the attributes of the DynamicsConstrains as a dict

        """
        return {'dynamicsShape':self.shape,'value':str(self.value),'dynamicsDimension':str(self.dimension)}

    def get_element(self,name='TransitionDynamics'):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element(name,self.get_attributes())

class DynamicsConstrains():
    """ DynamicsConstrains is used by triggers
        
        Parameters
        ----------
            max_acceleration (float): maximum acceleration allowed

            max_deceleration (float): maximum deceleration allowed

            max_speed (float): maximum speed allowed

        Attributes
        ----------
            max_acceleration (float): maximum acceleration allowed

            max_deceleration (float): maximum deceleration allowed

            max_speed (float): maximum speed allowed

        Methods
        -------
            is_filled()
                check is any constraints are set

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, max_acceleration=None, max_deceleration=None, max_speed=None):
        """ initalize DynamicsConstrains

        """

        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.max_speed = max_speed

    def is_filled(self):
        """ is_filled check is any constraints are set

            Returns: boolean

        """

        if self.max_acceleration or self.max_deceleration or self.max_speed:
            return True
        else:
            return False

    def get_attributes(self):
        """ returns the attributes of the DynamicsConstrains as a dict

        """
        retdict = {}
        if self.max_speed:
            retdict['maxSpeed'] = str(self.max_speed)
        if self.max_deceleration:
            retdict['maxDeceleration'] = str(self.max_deceleration)
        if self.max_acceleration:
            retdict['maxAcceleration'] = str(self.max_acceleration)
        return retdict

    def get_element(self,name = 'DynamicConstraints'):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element(name,attrib=self.get_attributes())


class Route():
    """ the Route class creates a route, needs atleast two waypoints to be valid
        
        Parameters
        ----------
            name (str): name of the Route

            closed (boolean): if the waypoints forms a loop
                Default: False

        Attributes
        ----------
            name (str): name of the Route

            closed (boolean): if the waypoints forms a loop
            
            waypoints (list of Waypoint): a list of waypoints

            parameters (ParameterDeclarations)

        Methods
        -------
            add_waypoint(waypoint)
                adds a waypoint to the route (minimum two)

            add_parameter(Parameter)
                adds a parameter to the route

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, name, closed=False):
        """ initalize Route

            Parameters
            ----------
                name (str): name of the Route

                closed (boolean): if the waypoints forms a loop
                    Default: False

        """
        self.name = name
        self.closed = closed
        self.waypoints = []
        self.parameters = ParameterDeclarations()


    def add_parameter(self,parameter):
        """ adds a parameter to the Route

            Parameters
            ----------
                parameter (Parameter): the parameter to add

        """
        self.parameters.add_parameter(parameter)

    def add_waypoint(self,position,strategy):
        """ adds a waypoint to the Route

            Parameters
            ----------
                position (*Position): any position for the route

                routestrategy (str): routing strategy for this waypoint

        """
        self.waypoints.append(Waypoint(position,strategy))

    def get_attributes(self):
        """ returns the attributes of the Route as a dict

        """
        retdict = {}
        retdict['name'] = self.name
        retdict['closed'] = str(self.closed)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Route

        """
        if len(self.waypoints) <2:
            ValueError('Too few waypoints')
        element = ET.Element('Route',attrib=self.get_attributes())
        element.append(self.parameters.get_element())
        for w in self.waypoints:
            element.append(w.get_element())
        return element

class Waypoint():
    """ the Route class creates a route, needs atleast two waypoints to be valid
        
        Parameters
        ----------
            position (*Position): any position for the route

            routestrategy (str): routing strategy for this waypoint

        Attributes
        ----------
            position (*Position): any position for the route

            routestrategy (str): routing strategy for this waypoint

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, position, routestrategy):
        """ initalize the Waypoint

            Parameters
            ----------
                position (*Position): any position for the route

                routestrategy (str): routing strategy for this waypoint

        """
        self.position = position
        self.routestrategy = routestrategy


    def get_attributes(self):
        """ returns the attributes of the Waypoint as a dict

        """
        return {'routeStrategy':self.routestrategy}

    def get_element(self):
        """ returns the elementTree of the Waypoint

        """
        element = ET.Element('Waypoint',attrib=self.get_attributes())
        element.append(self.position.get_element())
        return element


class Polyline():
    """ the Polyline class creates a polyline of (minimum 2) positions
        
        Parameters
        ----------
            time (list of double): a list of timings for the positions

            positions (list of positions): list of positions to create the polyline

        Attributes
        ----------
            time (*Position): any position for the route

            positions (str): routing strategy for this waypoint

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """

    def __init__(self, time, positions):
        """ initalize the Polyline

            Parameters
            ----------
                time (list of double): a list of timings for the positions

                positions (list of positions): list of positions to create the polyline

        """
        if len(time) < 2:
            ValueError('not enough time inputs')
        if len(positions)<2:
            ValueError('not enough position inputs')
        if len(time) != len(positions):
            ValueError('time and positions are not the same lenght')
        
        self.positions = positions
        self.time = time

    def get_element(self):
        """ returns the elementTree of the Polyline

        """
        element = ET.Element('Polyline')
        for i in range(len(self.time)):
            vert = ET.SubElement(element,'Vertex',attrib={'time':str(self.time[i])})
            vert.append(self.positions[i].get_element())
        return element


