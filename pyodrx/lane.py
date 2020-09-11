import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import LaneType, LaneChange, RoadMarkWeight, RoadMarkColor
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
    """
    def __init__(self):
        """ initalize Lanes

        """
        self.lanesections = []
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
                        link.predecessor.add_link('successor',link.lane_id)
                        link.successor.add_link('predecessor',link[0].lane_id)
                        link.used = True
          
        self.lanesections.append(lanesection)

    def get_element(self):
        """ returns the elementTree of Lanes

        """
        element = ET.Element('lanes')
        for l in self.lanesections:
            element.append(l.get_element())
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

        """ 
        self.lane_id = None
        self.lane_type = lane_type
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        self.soffset = soffset
        self.roadmark = None
        self.links = _Links()

        
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
        """ set the lane id of the lane

        """
        self.lane_id = lane_id

    def add_roadmark(self,roadmark):
        """ add_roadmark adds a roadmark to the lane
        
        Parameters
        ----------
            roadmark (RoadMark): roadmark of the lane

        """
        self.roadmark = roadmark
        

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
        element.append(self.links.get_element())

        widthdict = {}
        widthdict['a'] = str(self.a)
        widthdict['b'] = str(self.b)
        widthdict['c'] = str(self.c)
        widthdict['d'] = str(self.d)
        widthdict['sOffset'] = str(self.soffset)

        ET.SubElement(element,'width',attrib=widthdict)
        if self.roadmark:
            element.append(self.roadmark.get_element())
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
    def __init__(self,marking_type,width,length=0,space=0,toffset=0,soffset=0,rule=None,color=RoadMarkColor.standard):
        """ initalizes the Lane

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
        self.marking_type = marking_type
        self.length = length
        self.space = space
        self.toffset = toffset
        self.rule = rule
        self.soffset = soffset
        self.width = width
        self.color = color
        self._line = RoadLine(self.width,self.length,self.space,self.toffset,self.soffset,self.rule,self.color)
        
        #TODO: add more inputs and check 1.5
        

    def get_attributes(self):
        """ returns the attributes of the Lane as a dict

        """
        retdict = {}
        retdict['sOffset'] = str(self.soffset)
        retdict['type'] = enum2str(self.marking_type)
        retdict['weight'] = enum2str(RoadMarkWeight.standard)
        retdict['color'] = enum2str(self.color)
        retdict['sOffset'] = str(self.soffset)
        retdict['width'] = str(self.width)
        retdict['laneChange'] = enum2str(LaneChange.none)
        retdict['height'] = str(2e-02)
        return retdict

    def get_element(self):
        """ returns the elementTree of the WorldPostion

        """
        element = ET.Element('roadMark',attrib=self.get_attributes())
        typeelement = ET.SubElement(element,'type', attrib={'name':enum2str(self.marking_type),'width':str(self.width)})
        typeelement.append(self._line.get_element())
        return element


