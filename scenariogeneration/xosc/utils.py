""" The utils module contains the rest of the classes, such as Parameters, Environment, Routes and so on.

"""
import os
import xml.etree.ElementTree as ET
from .helpers import printToFile

from .enumerations import ParameterType, Rule, ReferenceContext, DynamicsShapes, DynamicsDimension, RouteStrategy,XSI,XMLNS, VehicleCategory,PrecipitationType,CloudState
import datetime as dt

class _PositionType():
    """ helper class for typesetting
    """
    pass

class _TriggerType():
    """ helper class for typesetting
    """
    pass

class _ValueTriggerType():
    """ helper class for typesetting
    """
    pass

class _EntityTriggerType():
    """ helper class for typesetting
    """
    pass

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
        if not isinstance(parameter,Parameter):
            raise TypeError('parameter input is not of type Parameter')
        self.parameters.append(parameter)
    
    def get_element(self):
        """ returns the elementTree of the ParameterDeclarations

        """
        element = ET.Element('ParameterDeclarations')
        for p in self.parameters:
            element.append(p.get_element())
        return element

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

class Parameter():
    """ Parameter is a declaration of a ParameterDeclaration for declarations
        
        Parameters
        ----------
            name (str): name of parameter

            parameter_type (ParameterType): type of the parameter 

            value (str): value of the parameter

        Attributes
        ----------
            name (str): name of parameter

            parameter_type (ParameterType): type of the parameter

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

                parameter_type (ParameterType): type of the parameter

                value (str): value of the parameter

        """
        self.name = name
        if parameter_type not in ParameterType:
            raise ValueError('parameter_type not a valid type.')
        self.parameter_type = parameter_type
        self.value = value

    def get_attributes(self):
        """ returns the attributes of the Parameter as a dict

        """
        return {'name':self.name,'parameterType':self.parameter_type.name,'value':str(self.value)}

    def get_element(self):
        """ returns the elementTree of the Parameter

        """
        element = ET.Element('ParameterDeclaration',attrib=self.get_attributes())
        return element

class Orientation():
    """ Orientation describes the angular orientation of an entity
        
        Parameters
        ----------
            h (float): header 

            p (float): pitch

            r (float): roll

            reference (ReferenceContext): absolute or relative

        Attributes
        ----------
            h (float): header 

            p (float): pitch

            r (float): roll

            reference (ReferenceContext): absolute or relative

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
        """ initalize Orientation 
        
            Parameters
            ----------
                h (float): header 

                p (float): pitch

                r (float): roll

                reference (ReferenceContext): absolute or relative
        """
        self.h = h
        self.p = p
        self.r = r
        if reference is not None and reference not in ReferenceContext:
            raise TypeError('reference input is not of type ReferenceContext')
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
            retdict['type'] = self.ref.name
        
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the DynamicsConstrains

        """
        return ET.Element('Orientation',attrib=self.get_attributes())

class TransitionDynamics():
    """ TransitionDynamics is used to define how the dynamics of a change
        
        Parameters
        ----------
            shape (DynamicsShapes): shape of the transition

            dimension (DynamicsDimension): the dimension of the transition (rate, time or distance)

            value (float): the value of the dynamics (time rate or distance)


        Attributes
        ----------
            shape (DynamicsShapes): shape of the transition

            dimension (DynamicsDimension): the dimension of the transition (rate, time or distance)

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
                shape (DynamicsShapes): shape of the transition

                dimension (DynamicsDimension): the dimension of the transition (rate, time or distance)

                value (float): the value of the dynamics (time rate or distance)

        """
        if shape not in DynamicsShapes:
            raise TypeError(shape + '; is not a valid shape.')
        
        self.shape = shape
        if dimension not in DynamicsDimension:
            raise ValueError(dimension + ' is not a valid dynamics dimension')
        self.dimension = dimension
        self.value = value

    def get_attributes(self):
        """ returns the attributes of the DynamicsConstrains as a dict

        """
        return {'dynamicsShape':self.shape.name,'value':str(self.value),'dynamicsDimension':self.dimension.name}

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

            append_to_catalog(filename)
                adds the Route to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the Route

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
        if not isinstance(closed,bool):
            raise TypeError('closed input is not of type bool')
        self.closed = closed
        self.waypoints = []
        self.parameters = ParameterDeclarations()

    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the Controller to it
            
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
        """ adds the Controller to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()

    def add_parameter(self,parameter):
        """ adds a parameter to the Route

            Parameters
            ----------
                parameter (Parameter): the parameter to add

        """
        if not isinstance(parameter,Parameter):
            raise TypeError('parameter input is not of type Parameter')
        self.parameters.add_parameter(parameter)

    def add_waypoint(self,position,routestrategy):
        """ adds a waypoint to the Route

            Parameters
            ----------
                position (*Position): any position for the route

                routestrategy (RouteStrategy): routing strategy for this waypoint

        """
        # note: the checks for types are done in Waypoint
        self.waypoints.append(Waypoint(position,routestrategy))

    def get_attributes(self):
        """ returns the attributes of the Route as a dict

        """
        retdict = {}
        retdict['name'] = self.name
        retdict['closed'] = convert_bool(self.closed)
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

            routestrategy (RouteStrategy): routing strategy for this waypoint

        Attributes
        ----------
            position (*Position): any position for the route

            routestrategy (RouteStrategy): routing strategy for this waypoint

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

                routestrategy (RouteStrategy): routing strategy for this waypoint

        """
        if not isinstance(position,_PositionType):
            raise TypeError('position input not a valid Position')
        self.position = position
        if routestrategy not in RouteStrategy:
            ValueError('not a valid RouteStrategy')
        self.routestrategy = routestrategy


    def get_attributes(self):
        """ returns the attributes of the Waypoint as a dict

        """
        return {'routeStrategy':self.routestrategy.name}

    def get_element(self):
        """ returns the elementTree of the Waypoint

        """
        element = ET.Element('Waypoint',attrib=self.get_attributes())
        element.append(self.position.get_element())
        return element


class Trajectory():
    """ the Trajectory class creates a Trajectory, 
        
        Parameters
        ----------
            name (str): name of the trajectory

            closed (boolean): if the trajectory is closed at the end

        Attributes
        ----------
            name (str): name of the trajectory

            closed (boolean): if the trajectory is closed at the end

            parameters (ParameterDeclaration): parameters for the trajectory

            shapes (list of Polyline, Clothoid, or Nurbs): list of the different shapes building the trajectory

        Methods
        -------
            add_shape(Polyline, Clothoid, or Nurbs):
                adds a shape to the trajectory (only the same shape can be used)
            
            add_parameter(Parameter)
                adds a parameter to the route

            append_to_catalog(filename)
                adds the vehicle to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the vehicle
                
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, name, closed):
        """ initalize the Trajectory

            Parameters
            ----------
            name (str): name of the trajectory

            closed (boolean): if the trajectory is closed at the end

        """

        self.name = name
        if not isinstance(closed,bool):
            raise TypeError('closed input is not boolean')
        self.closed = closed
        self.parameters = ParameterDeclarations()
        self.shapes = []
    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the Controller to it
            
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
        """ adds the Controller to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()

    def add_shape(self,shape):
        """ adds a shape to the trajectory (only the same shape can be used)

            Parameters
            ----------
            shape (Polyline, Clothoid, or Nurbs): the shape to be added to the trajectory

        """
        if not (isinstance(shape,Polyline) or isinstance(shape,Clothoid) or isinstance(shape,Nurbs)):
            raise TypeError('shape input neither of type Polyline, Clothoid, or Nurbs')
        self.shapes.append(shape)

    def add_parameter(self,parameter):
        """ adds a parameter to the Trajectory

            Parameters
            ----------
                parameter (Parameter): the parameter to add

        """
        if not isinstance(parameter,Parameter):
            raise TypeError('input parameter is not of type Parameter')
        self.parameters.add_parameter(parameter)

    def get_attributes(self):
        """ returns the attributes of the Trajectory as a dict

        """
        retdict = {}
        retdict['name'] = self.name
        retdict['closed'] = convert_bool(self.closed)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Trajectory

        """
        element = ET.Element('Trajectory',attrib=self.get_attributes())
        element.append(self.parameters.get_element())
        shape = ET.SubElement(element,'Shape')
        for sh in self.shapes:
            shape.append(sh.get_element())
        return element


class TimeReference():
    """ the TimeReference class creates a TimeReference, 
        
        Parameters
        ----------
            referece_domain (ReferenceContext): absolute or relative time reference (must be combined with scale and offset)
                Default: None
            scale (double): scalefactor of the timeings (must be combined with referece_domain and offset)
                Default: None
            offset (double): offset for time values (must be combined with referece_domain and scale)
                Default: None

        Attributes
        ----------
            referece_domain (str): absolute or relative time reference 

            scale (double): scalefactor of the timeings 

            offset (double): offset for time values 

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class
    """

    def __init__(self, reference_domain=None,scale=None,offset=None):
        """ initalize the TimeReference

            Parameters
            ----------
            referece_domain (ReferenceContext): absolute or relative time reference (must be combined with scale and offset)
                Default: None
            scale (double): scalefactor of the timeings (must be combined with referece_domain and offset)
                Default: None
            offset (double): offset for time values (must be combined with referece_domain and scale)
                Default: None

        """
        nones = [reference_domain == None, scale == None, offset == None]
        if sum(nones) == 3:
            self._only_nones = True
        elif sum(nones) == 0:
            self._only_nones = False
        else:
            raise ValueError('missing inputs for time reference')
        if reference_domain is not None and reference_domain not in ReferenceContext:
            raise TypeError('input reference_domain is not of type ReferenceContext')
        
        self.reference_domain = reference_domain
        self.scale = scale
        self.offset = offset

    def get_attributes(self):
        """ returns the attributes of the TimeReference as a dict

        """
        retdict = {}
        retdict['domainAbsoluteRelative'] = self.reference_domain.name
        retdict['scale'] = str(self.scale)
        retdict['offset'] = str(self.offset)
        return retdict

    def get_element(self):
        """ returns the elementTree of the TimeReference

        """

        element = ET.Element('TimeReference')
        if self._only_nones:
            ET.SubElement(element,'None')
        else:
            ET.SubElement(element,'Timing',self.get_attributes())
        
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
            raise ValueError('not enough time inputs')
        if len(positions)<2:
            raise ValueError('not enough position inputs')
        if len(time) != len(positions):
            raise ValueError('time and positions are not the same lenght')
        for p in positions:
            if not isinstance(p,_PositionType):
                raise TypeError('position input is not a valid position')
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

class Clothoid():
    """ the Clothoid class creates a Clothoid shape
        
        Parameters
        ----------
            curvature (float): start curvature of the clothoid

            curvature_change (float): rate of clothoid curvature change

            length (float): lenght of clothoid

            startposition (*Position): start position of the clothoid

            starttime (float): (optional) start time of the clothoid

            stoptime (float): (optional) end time of the clothoid

        Attributes
        ----------
            curvature (float): start curvature of the clothoid

            curvature_change (float): rate of clothoid curvature change

            length (float): lenght of clothoid

            startposition (*Position): start position of the clothoid

            starttime (float): (optional) start time of the clothoid

            stoptime (float): (optional) end time of the clothoid

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, curvature, curvature_change, length, startposition, starttime = None, stoptime = None):
        """ initalize the Clothoid

        Parameters
        ----------
            curvature (float): start curvature of the clothoid

            curvature_change (float): rate of clothoid curvature change

            length (float): lenght of clothoid

            startposition (*Position): start position of the clothoid

            starttime (float): (optional) start time of the clothoid

            stoptime (float): (optional) end time of the clothoid

        """

        
        self.curvature = curvature
        self.curvature_change = curvature_change
        self.length = length
        if not isinstance(startposition,_PositionType):
            raise TypeError('position input is not a valid position')
        self.startposition = startposition
        
        self.starttime = starttime
        self.stoptime = stoptime
        if (self.starttime == None and self.stoptime != None) or (self.starttime != None and self.stoptime == None):
            raise ValueError('Both start and stoptime has to be set, or none of them')
    
    def get_attributes(self):
        """ returns the attributes as a dict of the Clothoid

        """
        retdict = {}
        retdict['curvature'] = str(self.curvature)
        retdict['curvatureDot'] = str(self.curvature_change)
        retdict['length'] = str(self.length)
        if self.starttime != None:
            retdict['startTime'] = str(self.starttime)
            retdict['stopTime'] = str(self.stoptime)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Clothoid

        """
        element = ET.Element('Clothoid',attrib=self.get_attributes())
        element.append(self.startposition.get_element())

        return element

class ControlPoint():
    """ the ControlPoint class is used by Nurbs to define points 
        
        Parameters
        ----------
            position (*Position): a position for the point

            time (float): optional time specification of the point
                Default: None

            weight (float): optional weight of the point
                Default: None

        Attributes
        ----------
            position (*Position): a position for the point

            time (float): optional time specification of the point

            weight (float): optional weight of the point

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, position, time = None, weight = None):
        """ initalize the ControlPoint

        Parameters
        ----------
            position (*Position): a position for the point

            time (float): optional time specification of the point
                Default: None

            weight (float): optional weight of the point
                Default: None

        """

        if not isinstance(position,_PositionType):
            raise TypeError('position input is not a valid position')
        self.position = position
        self.time = time
        self.weight = weight
    
    def get_attributes(self):
        """ returns the attributes as a dict of the ControlPoint

        """
        retdict = {}
        if self.time:
            retdict['time'] = str(self.time)
        if self.weight:
            retdict['weight'] = str(self.weight)
        return retdict

    def get_element(self):
        """ returns the elementTree of the ControlPoint

        """
        element = ET.Element('ControlPoint',attrib=self.get_attributes())
        element.append(self.position.get_element())
        return element

class Nurbs():
    """ the Nurbs class creates a Nurbs shape
        
        Parameters
        ----------
            order (int): order of the nurbs

        Attributes
        ----------
            order (int): order of the nurbs

            controlpoints (list of *ControlPoint): a list of control point createing the nurbs 

            knots (list of double): knots of the nurbs (must be order + len(controlpoints)) in decending order

        Methods
        -------
            add_knots(knots)
                Adds the knots to the nurbs

            add_control_point(controlpoint)
                Adds a control point to the nurbs

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self, order):
        """ initalize the Nurbs

        Parameters
        ----------
            order (int): order of the nurbs

        """

        
        self.order = order
        self.controlpoints = []
        self.knots = []
    
    def add_knots(self,knots):
        """ adds a list of knots to the Nurbs

            Parameters
            ----------
                knots (list of double): knots of the nurbs (must be order + len(controlpoints)) in decending order
        """
        self.knots = knots
    def add_control_point(self,controlpoint):
        """ adds a controlpoint to the Nurbs

            Parameters
            ----------
                controlpoint (ControlPoint): a contact point to add to the nurbs
        """
        if not isinstance(controlpoint,ControlPoint):
            raise TypeError('controlpoint input is not of type ControlPoint')
        self.controlpoints.append(controlpoint)

    def get_attributes(self):
        """ returns the attributes as a dict of the Nurbs

        """
        retdict = {}
        retdict['order'] = str(self.order)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Nurbs

        """
        element = ET.Element('Nurbs',attrib=self.get_attributes())
        if (len(self.controlpoints) + self.order) != len(self.knots):
            raise ValueError('Number of knots is not equal to the number of contactpoints + order')
        for c in self.controlpoints:
            element.append(c.get_element())
        for k in self.knots:
            ET.SubElement(element,'Knot',attrib={'value':str(k)})
        

        return element




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
        """ returns the attributes as a dict of the FileHeader

        """
        return {'description':self.name,'author':self.author,'revMajor':'1','revMinor':'0','date':dt.datetime.now().isoformat()}

    def get_element(self):
        """ returns the elementTree of the FileHeader

        """
        element = ET.Element('FileHeader',attrib=self.get_attributes())

        return element



class _TrafficSignalState():
    """ crates a _TrafficSignalState used by Phase
        
        Parameters
        ----------
            signal_id (str): id of the traffic signal

            state (str): state of the signal
                
        Attributes
        ----------
            signal_id (str): id of the traffic signal

            state (str): state of the signal

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    
    def __init__(self, signal_id, state):
        """ initalize the _TrafficSignalState 
        
        Parameters
        ----------
            signal_id (str): id of the traffic signal

            state (str): state of the signal

        """
        
        self.signal_id = signal_id
        self.state = state

    def get_attributes(self):
        """ returns the attributes of the _TrafficSignalState
        
        """
        retdict = {}
        retdict['id'] = self.signal_id
        retdict['state'] = self.state
        return retdict

    def get_element(self):
        """ returns the elementTree of the _TrafficSignalState

        """
        return ET.Element('TrafficSignalState',attrib=self.get_attributes())
        

    
class Phase():
    """ crates a Traffic light phase
        
        Parameters
        ----------
            name (str): if of the phase

            duration (float): duration of the phase
                
        Attributes
        ----------
            name (str): if of the phase

            duration (float): duration of the phase

            signalstates (list of _TrafficSignalState): traffic signal states

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            add_stignal_state(signal_id,state)
                add a traffic signal state
    """

    def __init__(self, name, duration):
        """ initalize the Phase 
        
        Parameters
        ----------
            name (str): if of the phase

            duration (float): duration of the phase

        """
        
        self.name = name
        self.duration = duration
        self.signalstates = []


    def add_signal_state(self,signal_id,state):
        """ Adds a phase of the traffic signal

            Parameters
            ----------
                signal_id (str): id of the traffic signal in the road network

                state (str): state of the signal defined in the road network

        """
        self.signalstates.append(_TrafficSignalState(signal_id,state))

    def get_attributes(self):
        """ returns the attributes of the TrafficSignalController
        
        """
        retdict = {}
        retdict['name'] = self.name
        retdict['duration'] = str(self.duration)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Polyline

        """
        element = ET.Element('Phase',attrib=self.get_attributes())
        for s in self.signalstates: 
            element.append(s.get_element())
        return element


class TrafficSignalController():
    """ the TrafficSignalController class creates a polyline of (minimum 2) positions
        
        Parameters
        ----------
            name (str): if of the trafic signal

            delay (float): delay of the phase shift
                Default: None

            reference (string): id to the controller in the roadnetwork
                Default: None

        Attributes
        ----------
            name (str): if of the trafic signal

            delay (float): delay of the phase shift
                Default: None
            reference (string): id to the controller in the roadnetwork
                Default: None

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            add_phase(Phase)
                add a phase to the trafficsitnal controller
    """

    def __init__(self, name, delay = None,reference = None):
        """ initalize the TrafficSignalController 
        
        Parameters
        ----------
            name (str): if of the trafic signal

            delay (float): delay of the phase shift
                Default: None

            reference (string): id to the controller in the RoadNetwork
                Default: None

        """
        
        self.name = name
        self.delay = delay
        self.reference = reference
        self.phases = []


    def add_phase(self,phase):
        """ Adds a phase of the traffic signal

            Parameters
            ----------
                phase (Phase): a phase of the trafficsignal

        """
        if not isinstance(phase,Phase):
            raise TypeError('phase input is not of type Phase')
        self.phases.append(phase)

    def get_attributes(self):
        """ returns the attributes of the TrafficSignalController
        
        """
        retdict = {}
        retdict['name'] = self.name
        if self.delay:
            retdict['delay'] = str(self.delay)
        if self.reference:
            retdict['reference'] = self.reference
        return retdict

    def get_element(self):
        """ returns the elementTree of the TrafficSignalController

        """
        element = ET.Element('TrafficSignalController',attrib=self.get_attributes())
        for ph in self.phases: 
            element.append(ph.get_element())
        return element



class TrafficDefinition():
    """ the TrafficDefinition class creates a TrafficDefinition used by the different TrafficActions
        
        Parameters
        ----------
            name (str): name of the traffic definition
       

        Attributes
        ----------
            name (str): name of the traffic definition

            vehicleweights (list of floats): The weights of the vehicle categories (VehicleCategoryDistribution-wight)

            vehiclecategories (list of VehicleCategory): the vehicle category ((VehicleCategoryDistribution-category))

            controllerweights (list of floats): The weights of the controllers

            controllers (list of Controller/CatalogReference): The controllers for the traffic


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            add_vehicle(vehiclecategory,weight)
                Adds a vehicle to the traffic definition

            add_controller(controller,weight)
                Adds a controller to the traffic definition
                
    """

    def __init__(self, name):
        """ initalize the TrafficDefinition 
        
        Parameters
        ----------
            name (str): name of the traffic definition

        """            
        
        self.name = name
        self.vehicleweights = [] 
        self.vehiclecategories = [] 
        self.controllerweights = []
        self.controllers = []
        



    def add_vehicle(self,vehiclecategory,weight):
        """ Adds a vehicle to the traffic distribution

            Parameters
            ----------
                vehiclecategory (VehicleCategory): vehicle category of the entity in the traffic

                weight (float): the corresponding weight for the distribution of the vehicle category

        """
        if vehiclecategory not in VehicleCategory:
            raise TypeError('vehcilecategory input is not of type VehcileCategory')
        self.vehiclecategories.append(vehiclecategory)
        self.vehicleweights.append(weight)

    def add_controller(self,controller,weight):
        """ Adds a controller to the traffic distribution

            Parameters
            ----------
                controller (Controller or CatalogReference): a controller or catalog reference to a controller

                weight (float): the corresponding weight for the controller

        """
        if not ( isinstance(controller,Controller) or isinstance(controller,CatalogReference)):
            raise TypeError('controller input not of type Controller or CatalogReference')
        self.controllers.append(controller)
        self.controllerweights.append(weight)
    
    def get_attributes(self):
        """ returns the attributes of the TrafficDefinition
        
        """
        retdict = {}
        retdict['name'] = self.name
        return retdict

    def get_element(self):
        """ returns the elementTree of the TrafficDefinition

        """
        if not self.controllers:
            ValueError('No controllers defined for the TrafficDefinition')
        if not self.vehiclecategories:
            ValueError('No Vehicles defined for the TrafficDefinition')
                
        element = ET.Element('TrafficDefinition',attrib=self.get_attributes())
        
        veh_element = ET.SubElement(element,'VehicleCategoryDistribution')
        for i in range(len(self.vehiclecategories)):
            ET.SubElement(veh_element,'VehicleCategoryDistributionEntry',attrib={'category': self.vehiclecategories[i].name,'weight': str(self.vehicleweights[i])})

        cnt_element = ET.SubElement(element,'ControllerDistribution')
        for i in range(len(self.controllers)):
            tmp_controller = ET.SubElement(cnt_element,'ControllerDistributionEntry',attrib={'weight':str(self.controllerweights[i])})
            tmp_controller.append(self.controllers[i].get_element())

        return element




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
        element = ET.Element('OpenSCENARIO',attrib={'xmlns:xsi':XMLNS,'xsi:noNamespaceSchemaLocation':'../../'+XSI})
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

            parameterassignments (list of ParameterAssignment): the parameter assignments for the given catalogreference

        Methods
        -------
            add_parameter_assignment(parameterref,value)
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
        self.parameterassignments = []

    def add_parameter_assignment(self,parameterref,value):
        """ add_parameter_assignment adds a parameter and value to the catalog reference

            Parameters
            ----------
                parameterref (str): name of the parameter

                value (str): assigned value of the parameter
        """
        self.parameterassignments.append(ParameterAssignment(parameterref,value))

    def get_attributes(self):
        """ returns the attributes of the CatalogReference as a dict

        """
        return {'catalogName':self.catalogname,'entryName':self.entryname}

    def get_element(self):
        """ returns the elementTree of the CatalogReference

        """
        element = ET.Element('CatalogReference',attrib=self.get_attributes())
        if self.parameterassignments:
            parameterassigns = ET.SubElement(element,'ParameterAssignments')
        for parass in self.parameterassignments:
            parameterassigns.append(parass.get_element())
        return element
        
    

class ParameterAssignment():
    """ ParameterAssignment creates an ParameterAssignment element of openscenario
        
        Parameters
        ----------
            parameterref (str): name of the parameter

            value (str): assigned value of the parameter


        Attributes
        ----------
            parameterref (str): name of the parameter

            value (str): assigned value of the parameter

        Methods
        -------

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,parameterref,value):
        """ initalize the ParameterAssignment

            Parameters
            ----------
                parameterref (str): name of the parameter

                value (str): assigned value of the parameter   
                
        """
        self.parameterref = parameterref
        self.value = value

    def get_attributes(self):
        """ returns the attributes of the ParameterAssignment as a dict

        """
        retdict = {}
        retdict['parameterRef'] = self.parameterref
        retdict['value'] = str(self.value)
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the ParameterAssignment

        """
        return ET.Element('ParameterAssignment',attrib=self.get_attributes())

class TimeOfDay():
    """ TimeOfDay creates an TimeOfDay element of openscenario
        
        Parameters
        ----------
            animation (bool): if animation should be used

            year (int): year

            month (int): month

            day (int): day

            hour (int): hour

            minute (int): minute

            second (int): second

        Attributes
        ----------
            animation (bool): if animation should be used

            year (int): year

            month (int): month

            day (int): day

            hour (int): hour

            minute (int): minute

            second (int): second

        Methods
        -------

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,animation,year,month,day,hour,minute,second):
        """ initalize the TimeOfDay

            Parameters
            ----------
                animation (bool): if animation should be used

                year (int): year

                month (int): month

                day (int): day

                hour (int): hour

                minute (int): minute

                second (int): second   
                
        """
        self.animation = animation 
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def get_attributes(self):
        """ returns the attributes of the TimeOfDay as a dict

        """
        dt = str(self.year) + '-' + '{:0>2}'.format(self.month) + '-' + '{:0>2}'.format(self.day) + 'T' + '{:0>2}'.format(self.hour) + ':' + '{:0>2}'.format(self.minute) + ':' +'{:0>2}'.format(self.second)
        return {'animation':str(self.animation),'dateTime':dt}

    def get_element(self):
        """ returns the elementTree of the TimeOfDay

        """
        return ET.Element('TimeOfDay',attrib=self.get_attributes())



class Weather():
    """ Weather creates an Weather element of openscenario
        
        Parameters
        ----------
            cloudstate (CloudState): cloudstate of the weather

            sun_intensity (int): intensity of the sun (in lux)

            sun_azimuth (int): azimuth of the sun 0 north, pi/2 east, pi south, 3/2pi west

            sun_elevation (int): sun elevation angle 0 x/y plane, pi/2 zenith

            precipitation (precipitationType): dry, rain or snow

            precipitation_intensity (double): intensity of precipitation (0...1)

            visual_fog_range (int): visual range of fog
                Default: 100000

            fog_bounding_box (BoundingBox): bounding box of fog
                Default: None

        Attributes
        ----------
            cloudstate (CloudState): cloudstate of the weather

            sun_intensity (int): intensity of the sun (in lux)

            sun_azimuth (int): azimuth of the sun 0 north, pi/2 east, pi south, 3/2pi west

            sun_elevation (int): sun elevation angle 0 x/y plane, pi/2 zenith

            precipitation (precipitationType): dry, rain or snow

            precipitation_intensity (double): intensity of precipitation (0...1)

            visual_fog_range (int): visual range of fog

            fog_bounding_box (BoundingBox): bounding box of fog

        Methods
        -------

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,cloudstate,sun_intensity,sun_azimuth,sun_elevation,precipitation,precipitation_intensity,visual_fog_range = 100000,fog_bounding_box = None):
        """ initalize the Weather

            Parameters
            ----------
                cloudstate (CloudState): cloudstate of the weather

                sun_intensity (double): intensity of the sun (in lux)

                sun_azimuth (double): azimuth of the sun 0 north, pi/2 east, pi south, 3/2pi west

                sun_elevation (double): sun elevation angle 0 x/y plane, pi/2 zenith

                precipitation (PrecipitationType): dry, rain or snow

                precipitation_intensity (double): intensity of precipitation (0...1)

                visual_fog_range (double): visual range of fog
                    Default: 100000

                fog_bounding_box (BoundingBox): bounding box of fog
                    Default: None  
                
        """
        if cloudstate not in CloudState:
            raise TypeError('cloudstate input is not of type CloudState')
        if precipitation not in PrecipitationType:
            raise TypeError('precipitation input is not of type PrecipitationType')
        if fog_bounding_box != None and not isinstance(fog_bounding_box, BoundingBox):
            raise TypeError('fog_bounding_box input is not of type BoundingBox')
        self.cloudstate = cloudstate 
        self.sun_intensity = sun_intensity
        self.sun_azimuth = sun_azimuth
        self.sun_elevation = sun_elevation
        self.precipitation = precipitation
        self.precipitation_intensity = precipitation_intensity
        self.visual_fog_range = visual_fog_range
        self.fog_bounding_box = fog_bounding_box

    def get_attributes(self):
        """ returns the attributes of the Weather as a dict

        """
        return {'cloudState':self.cloudstate.name}

    def get_element(self):
        """ returns the elementTree of the Weather

        """
        element = ET.Element('Weather',attrib=self.get_attributes())
        ET.SubElement(element,'Sun',attrib={'intensity':str(self.sun_intensity),'azimuth':str(self.sun_azimuth),'elevation':str(self.sun_elevation)})
        fog = ET.SubElement(element,'Fog',attrib={'visualRange':str(self.visual_fog_range)})
        if self.fog_bounding_box:
            fog.append(self.fog_bounding_box.get_element())
        ET.SubElement(element,'Precipitation',attrib={'precipitationType':self.precipitation.name,'intensity':str(self.precipitation_intensity)})
        return element


class RoadCondition():
    """ Weather creates an Weather element of openscenario
        
        Parameters
        ----------
            friction_scale_factor (double): scale factor of the friction

            properties (Properties): properties of the roadcondition
                Default: None

        Attributes
        ----------
            friction_scale_factor (double): scale factor of the friction

            properties (Properties): properties of the roadcondition

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,friction_scale_factor,properties = None):
        """ initalize the Weather

            Parameters
            ----------
                friction_scale_factor (double): scale factor of the friction

                properties (Properties): properties of the roadcondition
                    Default: None
                
        """
        self.friction_scale_factor = friction_scale_factor 
        if properties is not None and not isinstance(properties,Properties):
            raise TypeError('properties input is not of type Properties')
        self.properties = properties

    def get_attributes(self):
        """ returns the attributes of the RoadCondition as a dict

        """
        return {'frictionScaleFactor':str(self.friction_scale_factor)}

    def get_element(self):
        """ returns the elementTree of the RoadCondition

        """
        element = ET.Element('RoadCondition',attrib=self.get_attributes())
        if self.properties:
            element.append(self.properties.get_element())
        return element




class Environment():
    """ The Environment class creates a environment used by Environment
        
        Parameters
        ----------
            timeofday (TimeOfDay): time of day for the environment

            weather (Weather): weather of the environment

            roadcondition (RoadCondition): road condition of the environment

            parameters (ParameterDeclarations): the parameters to be used in the scenario
                Default: None

        Attributes
        ----------

            timeofday (TimeOfDay): time of day for the environment

            weather (Weather): weather of the environment

            roadcondition (RoadCondition): road condition of the environment

            parameters (ParameterDeclarations): the parameters to be used in the scenario

        Methods
        -------
            append_to_catalog(filename)
                adds the vehicle to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the vehicle

            get_element()
                Returns the full ElementTree of the class

    """

    def __init__(self, timeofday, weather, roadcondition, parameters = None):
        """ initalize the Environment

            Parameters
            ----------
                timeofday (TimeOfDay): time of day for the environment

                weather (Weather): weather of the environment

                roadcondition (RoadCondition): road condition of the environment

                parameters (ParameterDeclarations): the parameters to be used in the scenario
                    Default: None
        """
        if not isinstance(timeofday,TimeOfDay):
            raise TypeError('timeofday input is not of type TypeOfDay')
        if not isinstance(weather,Weather):
            raise TypeError('weather input is not of type Weather')
        if not isinstance(roadcondition,RoadCondition):
            raise TypeError('roadcondition input is not of type RoadCondition')
        if parameters is not None and not isinstance(parameters,ParameterDeclarations):
            raise TypeError('parameters input is not of type ParameterDeclarations')    
        self.timeofday = timeofday
        self.weather = weather
        self.roadcondition = roadcondition
        self.parameters = parameters


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
    def get_element(self):
        """ returns the elementTree of the Environment

        """
        element = ET.Element('Environment')
        element.append(self.timeofday.get_element())
        element.append(self.weather.get_element())
        element.append(self.roadcondition.get_element())
        if self.parameters:
            element.append(self.parameters.get_element())
        return element



class Controller():
    """ the Controller class creates a controller of openScenario

        Parameters
        ----------
            name (str): name of the object

            properties (Properties): properties of the controller
                
        Attributes
        ----------
            parameters (ParameterDeclaration): Parameter declarations of the vehicle

            properties (Properties): additional properties of the vehicle

        Methods
        -------
            add_parameter(parameter)
                adds a parameter declaration to the Controller

            append_to_catalog(filename)
                adds the vehicle to an existing catalog

            dump_to_catalog(filename,name,description,author)
                crates a new catalog with the vehicle

            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self ,name ,properties):
        """ initalzie the Controller Class

        Parameters
        ----------
            name (str): name of the object

            properties (Properties): properties of the Controller
        
        """
        self.name = name
        
        self.parameters = ParameterDeclarations()
        if not isinstance(properties,Properties):
            raise TypeError('properties input is not of type Properties')
        self.properties = properties

    def dump_to_catalog(self,filename,catalogtype,description,author):
        """ dump_to_catalog creates a new catalog and adds the Controller to it
            
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
        """ adds the Controller to an existing catalog

            Parameters
            ----------
                filename (str): path to the catalog file

        """
        cf = CatalogFile()
        cf.open_catalog(filename)
        cf.add_to_catalog(self)
        cf.dump()

    def add_parameter(self,parameter):
        """ adds a parameter declaration to the Controller

            Parameters
            ----------
                parameter (Parameter): A new parameter declaration for the Controller

        """
        if not isinstance(parameter,Parameter):
            raise TypeError('parameter input is not of type Parameter')
        self.parameters.add_parameter(parameter)

    def get_attributes(self):
        """ returns the attributes of the Controller as a dict

        """
        return {'name':self.name}

    def get_element(self):
        """ returns the elementTree of the Controller

        """
        element = ET.Element('Controller',attrib=self.get_attributes())
        element.append(self.parameters.get_element())
        element.append(self.properties.get_element())
        
        return element


class BoundingBox():
    """ the Dimensions describes the size of an entity

        Parameters
        ----------
            width (float): the width of the entity

            length (float): the lenght of the entity

            height (float): the height of the entity

            x_center (float): x distance from back axel to center

            y_center (float): y distance from back axel to center

            z_center (float): z distance from back axel to center
                

        Attributes
        ----------
            boundingbox (BoundingBox): the bounding box of the entity

            center (Center): the center of the object relative the the back axel

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,width,length,height,x_center,y_center,z_center):
        """ initalzie the Dimensions

        Parameters
        ----------
            width (float): the width of the entity

            length (float): the lenght of the entity

            height (float): the height of the entity

            x_center (float): x distance from back axel to center

            y_center (float): y distance from back axel to center

            z_center (float): z distance from back axel to center
        
        """
        self.boundingbox = Dimensions(width,length,height)
        self.center = Center(x_center,y_center,z_center)

    def get_element(self):
        """ returns the elementTree of the Dimensions

        """
        element = ET.Element('BoundingBox')
        element.append(self.center.get_element())
        element.append(self.boundingbox.get_element())
        return element

class Center():
    """ the Center Class creates a centerpoint for a bounding box, reference point of a vehicle is the back axel

        Parameters
        ----------
            x (float): x distance from back axel to center

            y (float): y distance from back axel to center

            z (float): z distance from back axel to center
                

        Attributes
        ----------
            x (float): x distance from back axel to center

            y (float): y distance from back axel to center

            z (float): z distance from back axel to center

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,x,y,z):
        """ initalzie the Center Class

        Parameters
        ----------
            x (float): x distance from back axel to center

            y (float): y distance from back axel to center

            z (float): z distance from back axel to center
        
        """
        self.x = x
        self.y = y
        self.z = z
    def get_attributes(self):
        """ returns the attributes as a dict of the Center

        """
        return {'x':str(self.x),'y':str(self.y),'z':str(self.z)}

    def get_element(self):
        """ returns the elementTree of the Center

        """
        element = ET.Element('Center',attrib=self.get_attributes())
        return element

class Dimensions():
    """ the Dimensions describes the size of an entity

        Parameters
        ----------
            width (float): the width of the entity

            length (float): the lenght of the entity

            height (float): the height of the entity
                

        Attributes
        ----------
            width (float): the width of the entity

            length (float): the lenght of the entity

            height (float): the height of the entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,width,length,height):
        """ initalzie the Dimensions

        Parameters
        ----------
            width (float): the width of the entity

            length (float): the lenght of the entity

            height (float): the height of the entity
        
        """
        self.width = width
        self.length = length
        self.height = height
    def get_attributes(self):
        """ returns the attributes as a dict of the Dimensions

        """
        return {'width':str(self.width),'length':str(self.length),'height':str(self.height)}

    def get_element(self):
        """ returns the elementTree of the Dimensions

        """
        element = ET.Element('Dimensions',attrib=self.get_attributes())
        return element

class Properties():
    """ the Properties contains are for user defined properties of an object               

        Attributes
        ----------
            files (list of str): arbitrary files with properties

            properties (list of tuple(str,str)): properties in name/value pairs

        Methods
        -------
            add_file(file)
                adds a file with properties

            add_property(name,value)
                adds a property pair, with name and value

            get_element()
                Returns the full ElementTree of the class

            
    """
    def __init__(self):
        """ initalzie the Properties

        """
        self.files = []
        self.properties = []

    def add_file(self,filename):
        """ adds a property file

        Parameters
        ----------
            filename (str): name of the file

        """

        self.files.append(filename)

    def add_property(self,name,value):
        """ adds a property pair

        Parameters
        ----------
            name (str): name of the property

            value (str): value of the property

        """
        self.properties.append((name,value))

    def get_element(self):
        """ returns the elementTree of the Properties

        """
        element = ET.Element('Properties')
        for p in self.properties:
            ET.SubElement(element,'Property',attrib={'name':p[0],'value':p[1]})
        for f in self.files:
            ET.SubElement(element,'File',attrib={'filepath':f})
        
        
        return element



def merge_dicts(*dict_args):
    """ Funciton to merge dicts 
    
    """
    retdict = {}
    for d in dict_args:
        retdict.update(d)

    return retdict

def convert_bool(value):
    if value:
        return 'true'
    else:
        return 'false'
