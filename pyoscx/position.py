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
            get_element()
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
        """ returns the atributes of the WorldPostion as a dict

        """
        return {'x':str(self.x),'y':str(self.y),'z':str(self.z),'h':str(self.h),'p':str(self.p),'r':str(self.r)}

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('Position')
        ET.SubElement(element,'WorldPosition',attrib=self.get_attributes())
        return element

class RelativePosition():
    """ the RelativePosition creates a RelativePosition of openScenario
        
        Parameters
        ----------
            entity (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            reference (str): relative to world or an object
                Default: 'world'

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
        Attributes
        ----------
            target (str): the entity to be relative to

            reference (str): relative to world or an object

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            orient (Orientation): the angular orientation of the entity


        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__ (self,entity,dx,dy,dz=None,reference='world',orientation = Orientation()):
        """ initalizes the RelativePosition

        Parameters
        ----------
            target (str): the entity to be relative to

            dx (float): relative x-coord

            dy (float): relative y-coord

            dz (float): relative z-coord

            reference (str): relative to world or an object
                Default: 'world'

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()

        """
        self.target = entity
        if reference not in ['world','object']:
            raise ValueError(reference + '; is not a valid reference type (world or object).')
        self.reference = reference
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.orient = orientation
        if self.reference == 'object':
            self._elementname = 'RelativeObjectPosition'
        else:
            self._elementname = 'RelativeWorldPosition'
        
    def get_attributes(self):
        """ returns the atributes of the RelativePosition as a dict

        """
        retdict = {}
        retdict['dx'] = str(self.dx)
        retdict['dy'] = str(self.dy)
        if self.dz:
            retdict['dz'] = str(self.dz)
        return retdict

    def get_element(self):
        """ returns the elementTree of the RelativePosition

        """
        element = ET.Element('Position')
        
            
        relpos = ET.SubElement(element,self._elementname,attrib=self.get_attributes())
        if self.orient.is_filled():
            relpos.append(self.orient.get_element())
        return element



class RoadPosition():
    """  the RoadPosition creates a RoadPosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            t (float): lateral offset of center

            reference_id (str): id of the road or object

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
            reference (str): what to be relative to, road or object
                Default: 'road'

        Attributes
        ----------
            s (float): length along road

            t (float): lateral offset of center

            id (str): id of the road or object

            orient (Orientation): the angular orientation of the entity
                Default: Orientation()
        
            reference (str): what to be relative to, road or object

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,s,t,reference_id,orientation=Orientation(),reference='road'):
        if reference not in ['road', 'object']:
            raise ValueError(reference + '; is not a valid reference type (road or object).')
        self.reference = reference
        self.s = s
        self.t = t
        self.id = reference_id
        self.orient = orientation

        if self.reference == 'object':
            self._elementname = 'RelativeRoadPosition'
        else:
            self._elementname = 'RoadPosition'
    
    def get_attributes(self):
        """ returns the atributes of the RoadPosition as a dict

        """
        retdict = {}
        if self.reference == 'road':
            retdict['roadId'] = self.id
            retdict['ds'] = str(self.s)
            retdict['dt'] = str(self.t)
            
        else:
            retdict['entityRef'] = self.id
            retdict['s'] = str(self.s)
            retdict['t'] = str(self.t)
                
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the RoadPosition

        """
        element = ET.Element('Position')
        
        roadpos = ET.SubElement(element,self._elementname,attrib=self.get_attributes())
        if self.orient.is_filled():
            element.append(self.orient.get_element())
        return element



class LanePosition():
    """ the LanePosition creates a LanePosition of openScenario
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            reference_id (str): id of the road or object

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
            reference (str): what to be relative to, road or object

        Attributes
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            id (str): id of the road or object

            orient (Orientation): the angular orientation of the entity
                Default: Orientation()
        
            reference (str): what to be relative to, road or object
        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """
    def __init__(self,s,offset,lane,reference_id,orientation=Orientation(),reference='road'):
        """ initalizes the LanePosition
        
        Parameters
        ----------
            s (float): length along road

            offset (float): offset from center of lane

            reference_id (str): id of the road or object

            orientation (Orientation): the angular orientation of the entity
                Default: Orientation()
        
            reference (str): what to be relative to, road or object
        """ 
        if reference not in ['road', 'object']:
            raise ValueError(reference + '; is not a valid reference type (road or object).')
        self.reference = reference
        self.s = s
        self.lane = lane
        self.offset = offset
        self.id = reference_id
        self.orient = orientation
    
    def get_attributes(self):
        """ returns the atributes of the LanePosition as a dict

        """
        retdict = {}
        if self.reference == 'road':
            retdict['roadId'] = self.id
            retdict['laneId'] = self.lane
            retdict['ds'] = str(self.s)
            retdict['offset'] = str(self.offset)
            
        else:
            retdict['entityRef'] = self.id
            retdict['s'] = str(self.s)
            retdict['offset'] = str(self.offset)
            retdict['dLane'] = str(self.lane)
        
        return retdict
    
    def get_element(self):
        """ returns the elementTree of the LanePosition

        """
        element = ET.Element('Position')
        if self.reference == 'object':
            elementname = 'RelativeLanePosition'
        else:
            elementname = 'LanePosition'
        lanepos = ET.SubElement(element,elementname,attrib=self.get_attributes())
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