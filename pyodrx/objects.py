import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import ObjectType, Orientation, Dynamic 


# =============================================================================
# class Objects():
#     """ creates the Lanes element of opendrive
#     
# 
#         Attributes
#         ----------
#             lane_sections (list of LaneSection): a list of all lanesections
# 
#         Methods
#         -------
#             get_element(elementname)
#                 Returns the full ElementTree of the class
# 
#             add_lanesection(lanesection)
#                 adds a lane section to Lanes
#     """
#     def __init__(self):
#         """ initalize Lanes
# 
#         """
#         self.objects = []
#     def add_object(self,road_object):
#         """ creates the Lanes element of opendrive
#     
# 
#         Parameters
#         ----------
#             lanesection (LaneSection): a LaneSection to add
# 
#             lanelink (LaneLinker): (optional) a LaneLink to add 
# 
#         """
#         if not isinstance(road_object, list):
#             self.objects.append(road_object)
#         else:
#             self.objects = self.objects+road_object
# 
#     def get_element(self):
#         """ returns the elementTree of Lanes
# 
#         """
#         element = ET.Element('objects')
#         for road_object in self.objects:
#             element.append(road_object.get_element())
#         return element
# =============================================================================


class Object():
    """ creates an Object

        Parameters
        ----------
            marking_type (RoadMarkType): the type of marking

            width (float): with of the line

            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)

        Attributes
        ----------
            marking_type (str): the type of marking

            width (float): with of the line

            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

            add_roadmark(roadmark)
                adds a new roadmark to the lane

    """
    def __init__(self,object_type,object_id,s,t,height,object_subtype=None,dynamic=Dynamic.no,name='defaultName',zOffset=0,validLength=0,orientation=Orientation.none,hdg=0,pitch=0,roll=0,width=None,length=None,radius=None):
        """ initalizes the Object

        Parameters
        ----------
            marking_type (str): the type of marking

            width (float): with of the line

            length (float): length of the line
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line
                Default: 'standard'

        """ 
        self.object_type = object_type
        self.object_id = object_id
        self.s = s
        self.t = t
        self.height = height
        
        self.object_subtype = object_subtype
        self.dynamic = dynamic
        self.name = name
        self.zOffset = zOffset
        self.validLength = validLength
        self.orientation = orientation
        self.hdg = hdg
        self.pitch = pitch
        self.roll = roll
        self.width = width
        self.length = length
        self.radius = radius
        
        #change default line values for broken lines 
        if radius is not None and (width is not None or length is not None):
            print ("Object with id",self.object_id,"was provided with radius, width and/or length. Provide either radius or width and length. Using radius as fallback.")
            self.width = None
            self.length = None
        elif width is not None and length is None:
            print ("Object with id",self.object_id,"was provided with width, but length is missing. Using 0 as fallback.")
            self.length = 0
        elif length is not None and width is None:
            print ("Object with id",self.object_id,"was provided with length, but width is missing. Using 0 as fallback.")
            self.width = 0
        elif radius is None and width is None and length is None:
            print ("Object with id",self.object_id,"was provided with no radius, width or length. Provide either radius or width and length. Using radius=0 as fallback.")
            self.radius = 0
        else:
            pass
            
    def get_attributes(self):
        """ returns the attributes of the Lane as a dict

        """
        retdict = {}
        retdict['type'] = enum2str(self.object_type)
        retdict['id'] = str(self.object_id)
        retdict['s'] = str(self.s)
        retdict['t'] = str(self.t)
        retdict['height'] = str(self.height)
        retdict['subtype'] = str(self.object_subtype)
        retdict['dynamic'] = enum2str(self.dynamic)
        retdict['name'] = str(self.name)
        retdict['zOffset'] = str(self.zOffset)
        retdict['validLength'] = str(self.validLength)
        retdict['hdg'] = str(self.hdg)        
        retdict['pitch'] = str(self.pitch)
        retdict['roll'] = str(self.roll)
        
        if self.orientation == Orientation.positive:
            retdict['orientation'] = '+'    
        elif self.orientation == Orientation.negative:
            retdict['orientation'] = '-'        
        else:
            retdict['orientation'] = enum2str(self.orientation)    
        
        if self.radius is not None:
            retdict['radius'] = str(self.radius)                    
        else:
            retdict['width'] = str(self.width)
            retdict['length'] = str(self.length)
        
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('object',attrib=self.get_attributes())
        return element