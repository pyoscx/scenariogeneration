""" the position module contains the positions defined by OpenSCENARIO

"""
import xml.etree.ElementTree as ET

from .utils import Orientation, CatalogReference, Route, Trajectory, _PositionType
from .exceptions import OpenSCENARIOVersionError, ToManyOptionalArguments, NotEnoughInputArguments


class WorldPosition(_PositionType):
    """ the WorldPostion creates a worldposition of openScenario
        
        Parameters
        ----------
            x (float): x-coord of the entity

            y (float): y-coord of the entity

            z (float): z-coord of the entity

            h (float): heading of the entity

            p (float): pitch of the entity

            r (float): roll of the entity

        Attributes
        ----------
            x (float): x-coord of the entity

            y (float): y-coord of the entity

            z (float): z-coord of the entity

            h (float): heading of the entity

            p (float): pitch of the entity

            r (float): roll of the entity

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,x=0,y=0,z=None,h=None,p=None,r=None):
        """ initalizes the WorldPosition

        Parameters
        ----------
            x (float): x-coord of the entity

            y (float): y-coord of the entity

            z (float): z-coord of the entity

            h (float): heading of the entity

            p (float): pitch of the entity

            r (float): roll of the entity
        """ 
        self.x = x
        self.y = y 
        self.z = z
        self.h = h
        self.p = p
        self.r = r

    def __eq__(self,other):
        if isinstance(other,WorldPosition):
            if self.get_attributes() == other.get_attributes():
               return True
        return False
    def get_attributes(self):
        """ returns the attributes of the WorldPostion as a dict

        """
        retdict = {'x':str(self.x),'y':str(self.y)}
        if self.z:
            retdict['z'] = str(self.z)
        if self.h:
            retdict['h'] = str(self.h)
        if self.p:
            retdict['p'] = str(self.p)
        if self.r:
            retdict['r'] = str(self.r)
        return retdict
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the WorldPostion

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
        """
        element = ET.Element(elementname)
        ET.SubElement(element,'WorldPosition',attrib=self.get_attributes())
        return element

class RelativeWorldPosition(_PositionType):
    """ the WorldRelativePosition creates a RelativePosition with the option of world as reference
        
        Parameters
        ----------
            entity (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Attributes
        ----------
            target (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            orient (Orientation): the angular orientation of the entity


        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__ (self,entity,dx,dy,dz,orientation = Orientation()):
        """ initalizes the RelativeWorldPosition

        Parameters
        ----------
            target (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()

        """
        self.target = entity
        self.dx = dx
        self.dy = dy
        self.dz = dz
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orient = orientation
    
    def __eq__(self,other):
        if isinstance(other,RelativeWorldPosition):
            if self.get_attributes() == other.get_attributes() and self.orient == other.orient:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the RelativeWorldPosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['dx'] = str(self.dx)
        retdict['dy'] = str(self.dy)
        retdict['dz'] = str(self.dz)
        return retdict

    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RelativeWorldPosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position

        """
        element = ET.Element(elementname)            
        relpos = ET.SubElement(element,'RelativeWorldPosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            relpos.append(self.orient.get_element())
        return element


class RelativeObjectPosition(_PositionType):
    """ the RelativeObjectPosition creates a RelativePosition with the option of object as reference
        
        Parameters
        ----------
            entity (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Attributes
        ----------
            target (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            orient (Orientation): the angular orientation of the entity


        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__ (self,entity,dx,dy,dz=None,orientation = Orientation()):
        """ initalizes the RelativeObjectPosition

        Parameters
        ----------
            target (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord
                Default: None

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()

        """
        self.target = entity
        self.dx = dx
        self.dy = dy
        self.dz = dz
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orient = orientation


    def __eq__(self,other):
        if isinstance(other,RelativeObjectPosition):
            if self.get_attributes() == other.get_attributes() and self.orient == other.orient:
                return True
        return False


    def get_attributes(self):
        """ returns the attributes of the RelativeObjectPosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['dx'] = str(self.dx)
        retdict['dy'] = str(self.dy)
        if self.dz != None:
            retdict['dz'] = str(self.dz)
        return retdict

    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RelativeObjectPosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)              
        relpos = ET.SubElement(element,'RelativeObjectPosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            relpos.append(self.orient.get_element())
        return element



class RoadPosition(_PositionType):
    """  the RoadPosition creates a RoadPosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            t (float): lateral offset of center

            reference_id (str): id of the road

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Attributes
        ----------
            s (float): length along road

            t (float): lateral offset of center

            id (str): id of the road

            orient (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,s,t,reference_id,orientation=Orientation()):
        """ initalize the RoadPosition
        
            Parameters
            ----------
                s (float): length along road

                t (float): lateral offset of center

                reference_id (int): id of the road

                orientation (Orientation): the angular orientation of the entity
                    Default: Orientation()

        """
        self.s = s
        self.t = t
        self.id = reference_id
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orient = orientation

    def __eq__(self,other):
        if isinstance(other,RoadPosition):
            if self.get_attributes() == other.get_attributes() and self.orient == other.orient:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the RoadPosition as a dict

        """
        retdict = {}
        retdict['roadId'] = str(self.id)
        retdict['s'] = str(self.s)
        retdict['t'] = str(self.t)                
        return retdict
    
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RoadPosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)
        roadpos = ET.SubElement(element,'RoadPosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            roadpos.append(self.orient.get_element())
        return element


class RelativeRoadPosition(_PositionType):
    """  the RelativeRoadPosition creates a RelativeRoadPosition of openScenario
        
        Parameters
        ----------
            ds (float): length along road

            dt (float): lateral offset of center

            entity (str): id of the entity

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Attributes
        ----------
            ds (float): length along road

            dt (float): lateral offset of center

            target (str): id of the entity

            orient (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,ds,dt,entity,orientation=Orientation()):
        """ initalize the RelativeRoadPosition
        
            Parameters
            ----------
                ds (float): length along road

                dt (float): lateral offset of center

                entity (str): id of the entity

                orientation (Orientation): the angular orientation of the entity
                    Default: Orientation()

        """
        self.ds = ds
        self.dt = dt
        self.target = entity
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orient = orientation
    
    def __eq__(self,other):
        if isinstance(other,RelativeRoadPosition):
            if self.get_attributes() == other.get_attributes() and self.orient == other.orient:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the RelativeRoadPosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['ds'] = str(self.ds)
        retdict['dt'] = str(self.dt)
        return retdict
    
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RelativeRoadPosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)    
        roadpos = ET.SubElement(element,'RelativeRoadPosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            roadpos.append(self.orient.get_element())
        return element

class LanePosition(_PositionType):
    """ the LanePosition creates a LanePosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            lane_id (int): lane of the road

            road_id (int): id of the road           

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()    

        Attributes
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            lane_id (int): lane of the road

            road_id (int): id of the road

            orient (Orientation): the angular orientation of the entity
                Default: Orientation()

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,s,offset,lane_id,road_id,orientation=Orientation()):
        """ initalizes the LanePosition
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane
            
            lane_id (int): lane of the road

            road_id (int): id of the road           

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()  
        
        """ 
        self.s = s
        self.lane_id = lane_id
        self.offset = offset
        self.road_id = road_id
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orient = orientation
    
    def __eq__(self,other):
        if isinstance(other,LanePosition):
            if self.get_attributes() == other.get_attributes() and self.orient == other.orient:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the LanePosition as a dict

        """
        retdict = {}
        retdict['roadId'] = str(self.road_id)
        retdict['laneId'] = str(self.lane_id)
        retdict['s'] = str(self.s)
        retdict['offset'] = str(self.offset)
                   
        return retdict
    
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the LanePosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)    
        lanepos = ET.SubElement(element,'LanePosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            lanepos.append(self.orient.get_element())
        return element


class RelativeLanePosition(_PositionType):
    """ the RelativeLanePosition creates a RelativeLanePosition of openScenario
        
        Parameters
        ----------
            lane_id (str): lane of the road

            entity (str): id of the entity  

            offset (float): offset from center of lane             
                Default: 0

            ds (float): length along road (use this or dsLane)
                Default: None

            dsLane (double): relative offset along the lane (valid from V1.1) (use this or ds)
                Default: None

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()    

        Attributes
        ----------
            ds (float): length along road

            dsLane (double): relative offset along the lane (valid from V1.1)

            offset (float): offset from center of lane

            road_id (str): id of the road

            lane_id (str): lane of the road

            orient (Orientation): the angular orientation of the entity
                Default: Orientation()

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,lane_id,entity,offset=0,ds=None,dsLane=None,orientation=Orientation()):
        """ initalizes the RelativeLanePosition
        
        Parameters
        ----------
            lane_id (str): lane of the road

            entity (str): id of the entity  

            offset (float): offset from center of lane             
                Default: 0

            ds (float): length along road (use this or dsLane)
                Default: None

            dsLane (double): relative offset along the lane (valid from V1.1) (use this or ds)
                Default: None

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()    
        
        """ 
        if ds != None and dsLane != None:
            raise ToManyOptionalArguments('Not both of ds and dsLane can be used.')
        if ds == None and dsLane == None:
            raise NotEnoughInputArguments('Either ds or dsLane is needed as input.')
        self.ds = ds
        self.dsLane = dsLane
        self.lane_id = lane_id
        self.offset = offset
        self.entity = entity
        
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orient = orientation
    
    def __eq__(self,other):
        if isinstance(other,RelativeLanePosition):
            if self.get_attributes() == other.get_attributes() and self.orient == other.orient:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the RelativeLanePosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.entity
        if self.ds:
            retdict['ds'] = str(self.ds)
        if self.dsLane and not self.isVersion(minor=0):
            retdict['dsLane'] = str(self.dsLane)
        elif self.dsLane and self.isVersion(minor=0):
            OpenSCENARIOVersionError('dsLane was introduced in OpenSCENARIO V1.1, not in 1.0')
        retdict['offset'] = str(self.offset)
        retdict['dLane'] = str(self.lane_id)
        return retdict
    
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RelativeLanePosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)    
        lanepos = ET.SubElement(element,'RelativeLanePosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            lanepos.append(self.orient.get_element())
        return element


class RoutePositionOfCurrentEntity(_PositionType):
    """ RoutePositionOfCurrentEntity creates a RoutePosition with the InRoutePosition of type PositionOfCurrentEntity
        
        Parameters
        ----------
            route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

            entity (str): reference to the entity on the route

            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Attributes
        ----------
            route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

            entity (str): reference to the entity on the route

            orientation (Orientation): Oritation of the entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self,route_ref,entity,orientation = Orientation()):
        """ Initalize the RoutePositionOfCurrentEntity class
        
            Parameters
            ----------
                route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

                entity (str): reference to the entity on the route

                orientation (Orientation): Oritation of the entity
                    Default: Orientation()
        """
        if not ( isinstance(route_ref,Route) or isinstance(route_ref,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.route_ref = route_ref
        self.entity = entity
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orientation = orientation

    def __eq__(self,other):
        if isinstance(other,RoutePositionOfCurrentEntity):
            if self.entity == other.entity and self.orientation == other.orientation and self.route_ref == other.route_ref:
                return True
        return False
 
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RoutePositionOfCurrentEntity

        """
        element = ET.Element(elementname)
        relement = ET.SubElement(element,'RoutePosition')
        routeref = ET.SubElement(relement,'RouteRef')
        routeref.append(self.route_ref.get_element())
        relement.append(self.orientation.get_element())
        inroute = ET.SubElement(relement,'InRoutePosition')
        ET.SubElement(inroute,'PositionOfCurrentEntity',attrib={'entityRef':self.entity})
        return element



class RoutePositionInRoadCoordinates(_PositionType):
    """ RoutePositionInRoadCoordinates creates a RoutePosition with the InRoutePosition of type PositionInRoadCooardinates
        
        Parameters
        ----------
            route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

            s (double): s coordinate of the road

            t (double): t coordinate of the road

            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Attributes
        ----------
            route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

            s (double): s coordinate of the road

            t (double): t coordinate of the road

            orientation (Orientation): Oritation of the entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self, route_ref, s, t, orientation = Orientation()):
        """ Initalize the RoutePositionInRoadCoordinates class
        
            Parameters
            ----------
                route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

                s (double): s coordinate of the road

                t (double): t coordinate of the road

                orientation (Orientation): Oritation of the entity
                    Default: Orientation()
        """
        if not ( isinstance(route_ref,Route) or isinstance(route_ref,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.route_ref = route_ref
        self.s = s
        self.t = t
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orientation = orientation

    def __eq__(self,other):
        if isinstance(other,RoutePositionInRoadCoordinates):
            if self.s == other.s and self.t == other.t and self.orientation == other.orientation and self.route_ref == other.route_ref:
                return True
        return False

    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RoutePositionInRoadCoordinates

        """
        element = ET.Element(elementname)
        relement = ET.SubElement(element,'RoutePosition')
        routeref = ET.SubElement(relement,'RouteRef')
        routeref.append(self.route_ref.get_element())
        relement.append(self.orientation.get_element())
        inroute = ET.SubElement(relement,'InRoutePosition')
        ET.SubElement(inroute,'PositionInRoadCoordinates',attrib={'pathS':str(self.s),'t':str(self.t)})
        return element


class RoutePositionInLaneCoordinates(_PositionType):
    """ RoutePositionInLaneCoordinates creates a RoutePosition with the InRoutePosition of type PositionInLaneCoordinates
        
        Parameters
        ----------
            route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

            s (double): s coordinate of the road

            laneid (str): t coordinate of the road

            offset (double): lateral offset relative to the lane
                Default: 0

            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Attributes
        ----------
            route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

            s (double): s coordinate of the road

            laneid (str): t coordinate of the road

            offset (double): lateral offset relative to the lane
                Default: 0

            orientation (Orientation): Oritation of the entity

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self, route_ref, s, laneid, offset, orientation = Orientation()):
        """ Initalize the RoutePositionInLaneCoordinates class
        
            Parameters
            ----------
                route_ref (Route, or CatalogReference): Reference to the route the position is calculated from

                s (double): s coordinate of the road

                laneid (str): t coordinate of the road

                offset (double): lateral offset relative to the lane
                    Default: 0

                orientation (Orientation): Oritation of the entity
                    Default: Orientation()
        """
        if not ( isinstance(route_ref,Route) or isinstance(route_ref,CatalogReference)):
            raise TypeError('route input not of type Route or CatalogReference') 
        self.route_ref = route_ref
        self.s = s
        self.laneid = laneid
        self.offset = offset
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orientation = orientation

    def __eq__(self,other):
        if isinstance(other,RoutePositionInLaneCoordinates):
            if self.s == other.s and self.laneid == other.laneid and self.offset == other.offset and\
            self.orientation == other.orientation and self.route_ref == other.route_ref:
                return True
        return False

    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RoutePositionInLaneCoordinates

        """
        element = ET.Element(elementname)
        relement = ET.SubElement(element,'RoutePosition')
        routeref = ET.SubElement(relement,'RouteRef')
        routeref.append(self.route_ref.get_element())
        relement.append(self.orientation.get_element())
        inroute = ET.SubElement(relement,'InRoutePosition')
        ET.SubElement(inroute,'PositionInLaneCoordinates',attrib={'pathS':str(self.s),'laneId':self.laneid,'laneOffset':str(self.offset)})
        return element


class TrajectoryPosition(_PositionType):
    """ TrajectoryPosition creates a TrajectoryPosition of OpenSCENARIO
        
        Parameters
        ----------
            trajectory (Trajector, or CatalogRef): t coordinate of the road

            s (double): s coordinate of the trajector

            t (double): s coordinate of the road (optional)
                Default: None
            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Attributes
        ----------
            trajectory (Trajector, or CatalogRef): t coordinate of the road

            s (double): s coordinate of the trajector

            t (double): s coordinate of the road (optional)
                Default: None
            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self, trajectory, s, t = None, orientation = Orientation()):
        """ Initalize the TrajectoryPosition class
        
            Parameters
            ----------
                trajectory (Trajector, or CatalogRef): t coordinate of the road

                s (double): s coordinate of the trajector

                t (double): s coordinate of the road (optional)
                    Default: None
                orientation (Orientation): Oritation of the entity
                    Default: Orientation()
        """
        if not ( isinstance(trajectory,Trajectory) or isinstance(trajectory,CatalogReference)):
            raise TypeError('trajectory input not of type Trajectory or CatalogReference') 
        self.trajectory = trajectory
        self.s = s
        self.t = t
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orientation = orientation

    def __eq__(self,other):
        if isinstance(other,TrajectoryPosition):
            if self.get_attributes() == other.get_attributes() and\
            self.orientation == other.orientation and self.trajectory == other.trajectory:
                return True
        return False
    
    def get_attributes(self):
        """ returns the attributes of the TrajectoryPosition as a dict

        """
        retdict = {}
        retdict['s'] = str(self.s)
        if self.t:
            retdict['t'] = str(self.t)
        return retdict

    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the TrajectoryPosition

        """
        if self.isVersion(minor=0):
            raise OpenSCENARIOVersionError('TrajectoryPosition was introduced in OpenSCENARIO V1.1')

        element = ET.Element(elementname)
        traj_element = ET.SubElement(element,'TrajectoryPosition',attrib=self.get_attributes())
        trajref_element = ET.SubElement(traj_element,'TrajectoryRef')
        trajref_element.append(self.trajectory.get_element())
        traj_element.append(self.orientation.get_element())
        
        return element


class GeoPosition(_PositionType):
    """ GeoPosition creates a GeoPosition of OpenSCENARIO 
        
        Parameters
        ----------
            latitue (double): latitude point on earth

            longitude (double): longitude point on earth

            height (double): height above surcae
                Default: None

            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Attributes
        ----------
            latitue (double): latitude point on earth

            longitude (double): longitude point on earth

            height (double): height above surcae
                Default: None

            orientation (Orientation): Oritation of the entity
                Default: Orientation()

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

    """
    def __init__(self, latitude, longitude, height = None, orientation = Orientation()):
        """ Initalize the GeoPosition class
        
            Parameters
            ----------
                latitue (double): latitude point on earth

                longitude (double): longitude point on earth

                height (double): height above surcae
                    Default: None

                orientation (Orientation): Oritation of the entity
                    Default: Orientation()
        """

        self.longitude = longitude
        self.latitude = latitude
        self.height = height
        if not isinstance(orientation,Orientation):
            raise TypeError('input orientation is not of type Orientation')
        self.orientation = orientation

    def __eq__(self,other):
        if isinstance(other,GeoPosition):
            if self.get_attributes() == other.get_attributes() and\
            self.orientation == other.orientation:
                return True
        return False
    
    def get_attributes(self):
        """ returns the attributes of the GeoPosition as a dict

        """
        retdict = {}
        retdict['longitude'] = str(self.longitude)
        retdict['latitude'] = str(self.latitude)
        if self.height:
            retdict['height'] = str(self.height)
        return retdict

    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the GeoPosition

        """
        if self.isVersion(minor=0):
            raise OpenSCENARIOVersionError('GeoPosition was introduced in OpenSCENARIO V1.1')

        element = ET.Element(elementname)
        traj_element = ET.SubElement(element,'GeoPosition',self.get_attributes())
        traj_element.append(self.orientation.get_element())
        
        return element
