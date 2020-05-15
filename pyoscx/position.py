import xml.etree.ElementTree as ET

from .utils import Orientation

class WorldPosition():
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
    def __init__(self,x=0,y=0,z=0,h=0,p=0,r=0):
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

    def get_attributes(self):
        """ returns the attributes of the WorldPostion as a dict

        """
        return {'x':str(self.x),'y':str(self.y),'z':str(self.z),'h':str(self.h),'p':str(self.p),'r':str(self.r)}

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



class RelativeWorldPosition():
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
        self.orient = orientation

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


class RelativeObjectPosition():
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
    def __init__ (self,entity,dx,dy,dz,orientation = Orientation()):
        """ initalizes the RelativeObjectPosition

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
        self.orient = orientation

    def get_attributes(self):
        """ returns the attributes of the RelativeObjectPosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['dx'] = str(self.dx)
        retdict['dy'] = str(self.dy)
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



class RoadPosition():
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

                reference_id (str): id of the road

                orientation (Orientation): the angular orientation of the entity
                    Default: Orientation()

        """
        self.s = s
        self.t = t
        self.id = reference_id
        self.orient = orientation
    
    def get_attributes(self):
        """ returns the attributes of the RoadPosition as a dict

        """
        retdict = {}
        retdict['roadId'] = self.id
        retdict['ds'] = str(self.s)
        retdict['dt'] = str(self.t)                
        return retdict
    
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RoadPosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)
        ET.SubElement(element,'RoadPosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            element.append(self.orient.get_element())
        return element


class RelativeRoadPosition():
    """  the RelativeRoadPosition creates a RelativeRoadPosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            t (float): lateral offset of center

            entity (str): id of the entity

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Attributes
        ----------
            s (float): length along road

            t (float): lateral offset of center

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
    def __init__(self,s,t,entity,orientation=Orientation()):
        """ initalize the RoadPosition
        
            Parameters
            ----------
                s (float): length along road

                t (float): lateral offset of center

                entity (str): id of the entity

                orientation (Orientation): the angular orientation of the entity
                    Default: Orientation()

        """
        self.s = s
        self.t = t
        self.target = entity
        self.orient = orientation
    
    def get_attributes(self):
        """ returns the attributes of the RelativeRoadPosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.target
        retdict['s'] = str(self.s)
        retdict['t'] = str(self.t)
        return retdict
    
    def get_element(self,elementname = 'Position'):
        """ returns the elementTree of the RelativeRoadPosition

            Parameters
            ----------
                elementname (str): used if another name is needed for the position
                    Default: Position
                    
        """
        element = ET.Element(elementname)    
        ET.SubElement(element,'RelativeRoadPosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            element.append(self.orient.get_element())
        return element

class LanePosition():
    """ the LanePosition creates a LanePosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            road_id (int): id of the road

            lane_id (int): lane of the road

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()    

        Attributes
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            road_id (int): id of the road

            lane_id (int): lane of the road

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

            road_id (int): id of the road

            lane_id (int): lane of the road

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()  
        
        """ 
        self.s = s
        self.lane_id = lane_id
        self.offset = offset
        self.road_id = road_id
        self.orient = orientation
    
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
        ET.SubElement(element,'LanePosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            element.append(self.orient.get_element())
        return element


class RelativeLanePosition():
    """ the RelativeLanePosition creates a RelativeLanePosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            entity (str): id of the entity

            lane_id (str): lane of the road

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()    

        Attributes
        ----------
            s (float): length along road

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
    def __init__(self,s,offset,lane_id,entity,orientation=Orientation()):
        """ initalizes the LanePosition
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            entity (str): id of the entity

            lane_id (str): lane of the road

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()  
        
        """ 
        self.s = s
        self.lane_id = lane_id
        self.offset = offset
        self.entity = entity
        self.orient = orientation
    
    def get_attributes(self):
        """ returns the attributes of the LanePosition as a dict

        """
        retdict = {}
        retdict['entityRef'] = self.entity
        retdict['ds'] = str(self.s)
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
        ET.SubElement(element,'RelativeLanePosition',attrib=self.get_attributes())
        if self.orient.is_filled():
            element.append(self.orient.get_element())
        return element


### to be done
class RoutePosition():
    """ 
        
        Parameters
        ----------
            
        Attributes
        ----------

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self):
        pass