""" The lane module contains the basic classes for Lanes and roadmarks

"""

import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import LaneType, LaneChange, RoadMarkWeight, RoadMarkColor, RoadMarkType, MarkRule 
from .links import _Links,_Link


class Lanes():
    """ creates the Lanes element of opendrive
    

        Attributes
        ----------
            lane_sections (list of LaneSection): a list of all lanesections

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            add_lanesection(lanesection)
                adds a lane section to Lanes

            add_laneoffset(laneoffset) 
                adds a lane offset to Lanes
    """
    def __init__(self):
        """ initalize Lanes

        """
        self.lanesections = []
        self.laneoffsets = []

    def __eq__(self, other):
        if isinstance(other,Lanes):
            if self.laneoffsets == other.laneoffsets and \
            self.lanesections == other.lanesections:
                return True
        return False

    def add_lanesection(self,lanesection, lanelinks=None):
        """ creates the Lanes element of opendrive    

        Parameters
        ----------
            lanesection (LaneSection): a LaneSection to add

            lanelink (LaneLinker): (optional) a LaneLink to add 

        """
        # add links to the lanes
        if lanelinks: 
            #loop over all links 
            if not isinstance(lanelinks, list):
                lanelinks = [lanelinks]
            for lanelink in lanelinks:
                for link in lanelink.links:
                    # check if link already added 
                    if not link.used:
                        link.predecessor.add_link('successor',link.successor.lane_id)
                        link.successor.add_link('predecessor',link.predecessor.lane_id)
                        link.used = True
          
        self.lanesections.append(lanesection)

    def add_laneoffset(self, laneoffset):
        """ adds a lane offset to Lanes

        Parameters
        ----------
            laneoffset (LaneOffset): a LaneOffset to add
        """
        if not isinstance(laneoffset, LaneOffset):
            raise TypeError('add_laneoffset requires a LaneOffset as input, not ' + str(type(laneoffset)))
        self.laneoffsets.append(laneoffset)

    def get_element(self):
        """ returns the elementTree of Lanes

        """
        element = ET.Element('lanes')
        for l in self.lanesections:
            element.append(l.get_element())
        for l in self.laneoffsets:
            element.append(l.get_element())
        return element

class LaneOffset():
    """ the LaneOffset class defines an overall lateral offset along the road, described as a third degree polynomial

        Parameters
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

        Attributes
        ----------
            s (float): s start coordinate of the elevation

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns the attributes of the class

    """
    def __init__(self, s=0, a=0, b=0, c=0, d=0):
        """ initalize the LaneOffset class

        Parameters
        ----------
            s (float): s start coordinate of the LaneOffset

            a (float): a coefficient of the polynomial

            b (float): b coefficient of the polynomial

            c (float): c coefficient of the polynomial

            d (float): d coefficient of the polynomial

        """
        self.s = s
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __eq__(self, other):
        if isinstance(other,LaneOffset):
            if self.get_attributes() == other.get_attributes():
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the LaneOffset
        """
    
        retdict = {}
        retdict['s'] = str(self.s)
        retdict['a'] = str(self.a)
        retdict['b'] = str(self.b)
        retdict['c'] = str(self.c)
        retdict['d'] = str(self.d)
        return retdict

    def get_element(self):
        """ returns the elementTree of the LaneOffset
        """
        element = ET.Element('laneOffset',attrib=self.get_attributes())
        
        return element

class LaneSection():
    """ Creates the LaneSection element of opendrive

        Parameters
        ----------
            s (float): start of lanesection

            centerlane (Lane): the centerline of the road

        Attributes
        ----------
            s (float): start of lanesection

            centerlane (Lane): the centerline of the road

            leftlanes (list of Lane): the lanes left to the center

            rightlanes (list of Lane): the lanes right to the center

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of class

            add_left_lane(Lane)
                adds a new lane to the left

            add_right_lane(Lane)
                adds a new lane to the right
    """

    def __init__(self,s,centerlane):
        """ initalize the LaneSection

            Parameters
            ----------
                s (float): start of lanesection

                centerlane (Lane): the centerline of the road
        """
        self.s = s
        self.centerlane = centerlane
        self.centerlane._set_lane_id(0)
        self.leftlanes = []
        self.rightlanes = []
        self._left_id = 1
        self._right_id = -1

    def __eq__(self, other):
        if isinstance(other,LaneSection):
            if self.get_attributes() == other.get_attributes() and \
            self.centerlane == other.centerlane and \
            self.leftlanes == other.leftlanes and \
            self.rightlanes == other.rightlanes:
                return True
        return False

    def add_left_lane(self,lane):
        """ adds a lane to the left of the center, add from center outwards

            Parameters
            ----------
                lane (Lane): the lane to add
        """
        lane._set_lane_id(self._left_id)
        self._left_id += 1
        self.leftlanes.append(lane)
    
    def add_right_lane(self,lane):
        """ adds a lane to the right of the center, add from center outwards

            Parameters
            ----------
                lane (Lane): the lane to add
        """
        lane._set_lane_id(self._right_id)
        self._right_id -= 1
        self.rightlanes.append(lane)

    def get_attributes(self):
        """ returns the attributes of the Lane as a dict

        """
        retdict = {}
        retdict['s'] = str(self.s)
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('laneSection',attrib=self.get_attributes())

        if self.leftlanes:
            left = ET.SubElement(element,'left')
            for l in self.leftlanes:
                left.append(l.get_element())


        center = ET.SubElement(element,'center')
        center.append(self.centerlane.get_element())

        if self.rightlanes:
            right = ET.SubElement(element,'right')
            for l in self.rightlanes:
                right.append(l.get_element())

        return element

class Lane():
    """ creates a Lane of opendrive

        the inputs are on the following format:
            f(s) = a + b*s + c*s^2 + d*s^3

        Parameters
        ----------
            
            lane_type (LaneType): type of lane
                Default: LaneType.driving

            a (float): a coefficient
                Default: 0

            b (float): b coefficient
                Default: 0

            c (float): c coefficient
                Default: 0

            d (float): d coefficient
                Default: 0

            soffset (float): soffset of lane
                Default: 0


        Attributes
        ----------
            lane_id (int): id of the lane (automatically assigned by LaneSection)
            
            lane_type (LaneType): type of lane

            a (float): a coefficient

            b (float): b coefficient

            c (float): c coefficient

            d (float): d coefficient

            soffset (float): soffset of lane

            roadmark (RoadMark): roadmarks related to the lane

            links (_Links): Lane links to the lane

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of class

            add_roadmark(roadmark)
                adds a new roadmark to the lane

    """
    def __init__(self,lane_type=LaneType.driving,a=0,b=0,c=0,d=0,soffset=0):
        """ initalizes the Lane

        Parameters
        ----------
            
            lane_type (LaneType): type of lane
                Default: LaneType.driving

            a (float): a polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            b (float): b polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            c (float): c polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            d (float): d polynomial coefficient for width (left/right) or laneoffset (center)
                Default: 0

            soffset (float): soffset of lane renamed to s in case of centerlane
                Default: 0

        """ 
        self.lane_id = None
        self.lane_type = lane_type
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.soffset = soffset
        #TODO: enable multiple widths records per lane (only then soffset really makes sense! ASAM requires one width record to have sOffset=0)
        self.heights = [] #height entries to elevate the lane independent from the road elevation 
        self.roadmark = None
        self.links = _Links()

    def __eq__(self, other):
        if isinstance(other,Lane):
            if self.links == other.links and \
            self.get_attributes() == other.get_attributes() and \
            self.a == other.a and \
            self.b == other.b and \
            self.c == other.c and \
            self.d == other.d and \
            self.soffset == other.soffset and \
            self.heights == other.heights and \
            self.roadmark == other.roadmark:
                return True
        return False
        
        #TODO: add more features to add for lane
    def add_link(self,link_type,id):
        """ adds a link to the lane section

        Parameters
        ----------
            link_type (str): type of link, successor or predecessor

            id (str/id): id of the linked lane
        """
        self.links.add_link(_Link(link_type,str(id)))

    def _set_lane_id(self,lane_id):
        """ set the lane id of the lane and set lane type to 'none' in case of centerlane

        """
        self.lane_id = lane_id
        if self.lane_id == 0:
            self.lane_type = LaneType.none

    def add_roadmark(self,roadmark):
        """ add_roadmark adds a roadmark to the lane
        
        Parameters
        ----------
            roadmark (RoadMark): roadmark of the lane

        """
        self.roadmark = roadmark
    
    def add_height(self, inner, outer=None, soffset=0):
        """ add_height adds a height entry to the lane to elevate it independent from the road elevation
        
        Parameters
        ----------
            inner (float): inner height
            
            outer (float): outer height (if not provided, inner height is used)
                Default: None
                
            s_offset (float): s offset of the height record
                Default: 0                

        """
        heightdict = {}
        heightdict['inner'] = str(inner)
        if outer is not None:
            heightdict['outer'] = str(outer)
        else:
            heightdict['outer'] = str(inner)
        heightdict['sOffset'] = str(soffset)
        
        self.heights.append(heightdict)
      
        

    def get_attributes(self):
        """ returns the attributes of the Lane as a dict

        """
        retdict = {}
        if self.lane_id == None:
            raise ValueError('lane id is not set correctly.')
        retdict['id'] = str(self.lane_id)
        retdict['type'] = enum2str(self.lane_type)
        retdict['level'] = 'false'
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('lane',attrib=self.get_attributes())
                
        #polynomial dict either for width (left/right lanes) or laneOffset (center lane)
        polynomialdict = {}
        polynomialdict['a'] = str(self.a)
        polynomialdict['b'] = str(self.b)
        polynomialdict['c'] = str(self.c)
        polynomialdict['d'] = str(self.d)
        polynomialdict['sOffset'] = str(self.soffset) 
        
        #according to standard if lane is centerlane it should 
        #not have a width record and omit the link record        
        if self.lane_id != 0: 
            element.append(self.links.get_element())
            ET.SubElement(element,'width',attrib=polynomialdict)        
        #use polynomial dict for laneOffset in case of center lane (only if values provided)
        # removed, should not be here..
        # elif any([self.a,self.b,self.c,self.d]):
        #     polynomialdict['s'] = polynomialdict.pop('sOffset')            
        #     ET.SubElement(element,'laneOffset',attrib=polynomialdict)                         
            
        if self.roadmark:
            element.append(self.roadmark.get_element())
            
        for height in self.heights:
            ET.SubElement(element,'height',attrib=height)
            
        return element

class RoadMark():
    """ creates a RoadMark of opendrive

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
    def __init__(self,marking_type,width=None,length=None,space=None,toffset=None,soffset=0,rule=None,color=RoadMarkColor.standard,marking_weight=RoadMarkWeight.standard,height=0.02,laneChange=None):
        """ initializes the RoadMark

        Parameters
        ----------
            marking_type (str): the type of marking          

            width (float): width of the marking / line
                Default: None
            length (float): length of the visible, marked part of the line
                Default: None
            space (float): length of the invisible, unmarked part of the line
                Default: None
            toffset (float): offset in t
                Default: None
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)
                Default: None
            color (RoadMarkColor): color of marking
                Default: 'standard'
            marking_weight (str): the weight of marking
                Default: standard
            height (float): thickness of marking
                Default: 0.02
            laneChange (LaneChange): indicates direction in which lane change is allowed
                Default: none

        """ 
        #required arguments - must be provided by user
        self.marking_type = marking_type
        
        #required arguments - must be provided by user or taken from defaults
        self.marking_weight = marking_weight
        self.color = color
        self.soffset = soffset
        self.height = height
        self.laneChange = laneChange

        #optional arguments - roadmark is valid without them being defined
        self.width = width
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = rule

            
        #TODO: there may be more line child elements per roadmark, which is currently unsupported
        self._line = None
        #check if arguments were passed that require line child element
        if any([length, space, toffset, rule]):
            #set defaults in case no values were provided
            #values for broken lines 
            if marking_type == RoadMarkType.broken: 
                self.length = length or 3
                self.space = space or 3
            #values for solid lines 
            elif marking_type == RoadMarkType.solid:
                self.length = length or 3
                self.space = space or 0
            #create empty line if arguments are missing
            else: 
                self.length = length or 0
                self.space = length or 0
                print ("No defaults for arguments 'space' and 'length' for roadmark type", enum2str(marking_type), "available and no values were passed. Creating an empty roadmark.")
            #set remaining defaults
            self.width = width or 0.2
            self.toffset = toffset or 0
            self.rule = rule or MarkRule.none
            self._line = RoadLine(self.width,self.length,self.space,self.toffset,self.soffset,self.rule,self.color)          

    def __eq__(self, other):
        if isinstance(other,RoadMark):
            if self._line == other._line and \
            self.get_attributes() == other.get_attributes() and \
            self.marking_type == other.marking_type:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes of the RoadMark as a dict

        """
        retdict = {}
        retdict['sOffset'] = str(self.soffset)
        retdict['type'] = enum2str(self.marking_type)
        retdict['weight'] = enum2str(self.marking_weight)
        retdict['color'] = enum2str(self.color)
        retdict['height'] = str(self.height)
        if self.width is not None:
            retdict['width'] = str(self.width)
        if self.laneChange is not None:
            retdict['laneChange'] = enum2str(self.laneChange)
        return retdict

    def get_element(self):
        """ returns the elementTree of the RoadMark

        """
        element = ET.Element('roadMark',attrib=self.get_attributes())
        if self._line != None:
            typeelement = ET.SubElement(element,'type', attrib={'name':enum2str(self.marking_type),'width':str(self.width)})
            typeelement.append(self._line.get_element())
        return element
        
class RoadLine():
    """ creates a Line type of to be used in roadmark

        Parameters
        ----------
            width (float): with of the line
                Default: 0
            length (float): length of the line
                Default: 0
            space (float): length of space between (broken) lines
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)

        Attributes
        ----------
            length (float): length of the line

            space (float): length of space between (broken) lines

            toffset (float): offset in t

            soffset (float): offset in s

            rule (MarkRule): mark rule

            width (float): with of the line

            color (RoadMarkColor): color of line

        Methods
        -------
            get_element(elementname)
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

    """
    # TODO: check this for 1.5
    def __init__(self,width = 0,length=0,space=0,toffset=0,soffset=0,rule=None,color=None):
        """ initalizes the RoadLine

        Parameters
        ----------
            width (float): with of the line
                Default: 0
            length (float): length of the line
                Default: 0
            space (float): length of space between (broken) lines
                Default: 0
            toffset (float): offset in t
                Default: 0
            soffset (float): offset in s
                Default: 0
            rule (MarkRule): mark rule (optional)

            color (RoadMarkColor): color of line (optional)


        """ 
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = rule
        self.soffset = soffset
        self.width = width
        self.color = color


    def __eq__(self, other):
        if isinstance(other,RoadLine):
            if self.get_attributes() == other.get_attributes():
                return True
        return False
        

    def get_attributes(self):
        """ returns the attributes of the Lane as a dict

        """
        retdict = {}
        retdict['length'] = str(self.length)
        retdict['space'] = str(self.space)
        retdict['tOffset'] = str(self.toffset)
        retdict['width'] = str(self.width)
        retdict['sOffset'] = str(self.soffset)
        # if self.color:
            # retdict['color'] = enum2str(self.color)
        if self.rule:
            retdict['rule'] = enum2str(self.rule)
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('line',attrib=self.get_attributes())
        return element



