""" the links module contains the basic classes and helpers for lane linking and junctions

"""
import xml.etree.ElementTree as ET
from .helpers import enum2str
from .enumerations import ElementType, JunctionGroupType

from .exceptions import NotSameAmountOfLanesError
import warnings

class _Links():
    """ Link creates a Link element used for roadlinking in OpenDrive
        
        Parameters
        ----------

        Attributes
        ----------
            links (_Link): all links added

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            add_link(link)
                adds a link to links

    """
    def __init__(self):
        """ initalize the _Links

        """

        self.links = []

    def __eq__(self, other):
        if isinstance(other,_Links):
            if self.links == other.links:
                return True
        return False

    def add_link(self,link):
        """ Adds a _Link 

            Parameters
            ----------
                link (_Link): a link to be added to the Links

        """
        if link in self.links:
            warnings.warn('Multiple identical links is detected, this might cause problems. Using the first one created. ',UserWarning)
        elif any([link.link_type == x.link_type for x in self.links]):
            warnings.warn('Multiple links of the same link_type: ' + link.link_type + ' is detected, this might cause problems, overwriting the old one. ',UserWarning)
            for l in self.links:
                if l == link.link_type:
                    self.links.remove(l)
            self.links.append(link)
        else:
            self.links.append(link)

    def get_predecessor_contact_point(self):
        """ returns the predecessor contact_point of the link (if exists)

            Return
                id (int): id of the predecessor road
        """
        retval = None
        for l in self.links:
            if l.link_type == 'predecessor':
                retval = l.contact_point
        return retval
    def get_successor_contact_point(self):
        """ returns the successor contact_point of the link (if exists)

            Return
                id (int): id of the successor road (None if no successor available)
        """
        retval = None
        for l in self.links:
            if l.link_type == 'successor':
                retval = l.contact_point
        return retval
    def get_predecessor_type(self):
        """ returns the predecessor id of the link (if exists)

            Return
                id (int): id of the predecessor road
        """
        retval = None
        for l in self.links:
            if l.link_type == 'predecessor':
                retval = l.element_type
        return retval
    def get_successor_type(self):
        """ returns the successor id of the link (if exists)

            Return
                id (int): id of the successor road (None if no successor available)
        """
        retval = None
        for l in self.links:
            if l.link_type == 'successor':
                retval = l.element_type
        return retval
    def get_predecessor_id(self):
        """ returns the predecessor id of the link (if exists)

            Return
                id (int): id of the predecessor road
        """
        retval = None
        for l in self.links:
            if l.link_type == 'predecessor':
                retval = l.element_id
        return retval

    def get_successor_id(self):
        """ returns the successor id of the link (if exists)

            Return
                id (int): id of the successor road (None if no successor available)
        """
        retval = None
        for l in self.links:
            if l.link_type == 'successor':
                retval = l.element_id
        return retval
    def get_element(self):
        """ returns the elementTree of the _Link

        """
        
        element = ET.Element('link')
        for l in self.links:
            element.append(l.get_element())
        return element


class _Link():
    """ Link creates a predecessor/successor/neghbor element used for Links in OpenDrive
        
        Parameters
        ----------
            link_type (str): the type of link (successor, predecessor, or neighbor)

            element_id (str): name of the linked road
            
            element_type (ElementType): type of element the linked road
                Default: None

            contact_point (ContactPoint): the contact point of the link
                Default: None

            direction (Direction): the direction of the link (used for neighbor)
                Default: None

        Attributes
        ----------
            link_type (str): the type of link (successor, predecessor, or neighbor)

            element_type (ElementType): type of element the linked road

            element_id (str): name of the linked road

            contact_point (ContactPoint): the contact point of the link (used for successor and predecessor)

            direction (Direction): the direction of the link (used for neighbor)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

    """

    def __init__(self,link_type,element_id,element_type=None,contact_point=None,direction=None):
        """ initalize the _Link

        Parameters
        ----------
            link_type (str): the type of link (successor, predecessor, or neighbor)

            element_id (str): name of the linked road
            
            element_type (ElementType): type of element the linked road
                Default: None

            contact_point (ContactPoint): the contact point of the link
                Default: None

            direction (Direction): the direction of the link (used for neighbor)
                Default: None
        """


        if link_type == 'neighbor':
            if direction == None:
                raise ValueError('direction has to be defined for neighbor')

        self.link_type = link_type
        self.element_type = element_type
        self.element_id = element_id
        self.contact_point = contact_point
        self.direction = direction

    def __eq__(self, other):
        if isinstance(other,_Link):
            if self.get_attributes() == other.get_attributes() and self.link_type == other.link_type:
                return True
        return False

    def get_attributes(self):
        """ returns the attributes as a dict of the _Link

        """
        retdict = {}
        if self.element_type == None:
            retdict['id'] = str(self.element_id)
        else:
            retdict['elementType'] = enum2str(self.element_type)
            retdict['elementId'] = str(self.element_id)
        
        if self.contact_point:
            retdict['contactPoint'] = enum2str(self.contact_point)
        elif self.link_type == 'neighbor':
            retdict['direction'] = enum2str(self.direction)
        return retdict

    def get_element(self):
        """ returns the elementTree of the _Link

        """
        element = ET.Element(self.link_type,attrib=self.get_attributes())
        return element

class LaneLinker():
    """ LaneLinker stored information for linking lane sections 
        NOTE: Not part of OpenDRIVE, but a helper to link lanes for the user.
        
        Parameters
        ----------

        Attributes
        ----------
            links: all lane links added (predlane (Lane), succlane (Lane), found=bool)

        Methods
        -------
            add_link(predlane, succlane)
                adds a lane link 

    """
    def __init__(self):
        """ initalize the _Links

        """

        self.links = []

    def add_link(self,predlane, succlane,connecting_road=None):
        """ Adds a _Link 

            Parameters
            ----------
                predlane (Lane): predecessor lane

                succlane (Lane): successor lane

                connecting_road (id): id of a connecting road (used for junctions)

        """
        self.links.append(_lanelink(predlane,succlane,connecting_road))

class _lanelink():
    """ helper class for LaneLinker

    """
    def __init__(self,predecessor,successor,connecting_road):
        self.predecessor = predecessor
        self.successor = successor
        self.connecting_road = connecting_road 
        self.used = False


class Connection():
    """ Connection creates a connection as a base of junction
        
        Parameters
        ----------
            incoming_road (int): the id of the incoming road to the junction

            connecting_road (int): id of the connecting road (type junction)
            
            contact_point (ContactPoint): the contact point of the link

            id (int): id of the junction (automated?)

        Attributes
        ----------
            incoming_road (int): the id of the incoming road to the junction

            connecting_road (int): id of the connecting road (type junction)
            
            contact_point (ContactPoint): the contact point of the link

            id (int): id of the connection (automated?)

            links (list of tuple(int) ): a list of all lanelinks in the connection

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            add_lanelink(in_lane,out_lane)
                Adds a lane link to the connection
    """

    def __init__(self,incoming_road,connecting_road,contact_point,id=None):
        """ initalize the Connection

        Parameters
        ----------
            incoming_road (int): the id of the incoming road to the junction

            connecting_road (int): id of the connecting road (type junction)
            
            contact_point (ContactPoint): the contact point of the link

            id (int): id of the junction (automated)
        """

        self.incoming_road = incoming_road
        self.connecting_road = connecting_road
        self.contact_point = contact_point
        self.id = id
        self.links = []

    def __eq__(self, other):
        if isinstance(other,Connection):
            if self.get_attributes() == other.get_attributes() and \
            self.links == other.links:
                return True
        return False

    def _set_id(self,id):
        """ id is set

            Parameters
            ----------
                id (int): the id of the connection
        """
        if self.id == None:
            self.id = id

    def add_lanelink(self,in_lane,out_lane):
        """ Adds a new link to the connection

            Parameters
            ----------
                in_lane: lane id of the incoming road

                out_lane: land id of the outgoing road
        """
        self.links.append((in_lane,out_lane))
    def get_attributes(self):
        """ returns the attributes as a dict of the Connection

        """
        retdict = {}
        retdict['incomingRoad'] = str(self.incoming_road)
        retdict['id'] = str(self.id)
        retdict['contactPoint'] = enum2str(self.contact_point)
        retdict['connectingRoad'] = str(self.connecting_road)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Connection

        """
        element = ET.Element('connection',attrib=self.get_attributes())
        for l in self.links:
            ET.SubElement(element,'laneLink',attrib={'from':str(l[0]),'to':str(l[1])})
        return element



class Junction():
    """ Junction creates a junction of OpenDRIVE
        
        Parameters
        ----------
            name (str): name of the junction

            id (int): id of the junction

        Attributes
        ----------
            name (str): name of the junction

            id (int): id of the junction

            connections (list of Connection): all the connections in the junction

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            add_connection(connection)
                Adds a connection to the junction
    """
    ##TODO: add type
    def __init__(self,name,id):
        """ initalize the Junction

        Parameters
        ----------
            name (str): name of the junction

            id (int): id of the junction
        """
        self.name = name
        self.id = id
        self.connections = []
        self._id_counter = 0

    def __eq__(self, other):
        if isinstance(other,Junction):
            if self.get_attributes() == other.get_attributes() and \
            self.connections == other.connections:
                return True
        return False

    def add_connection(self,connection):
        """ Adds a new link to the Junction

            Parameters
            ----------
                connection (Connection): adds a connection to the junction

        """
        connection._set_id(self._id_counter)
        self._id_counter += 1
        self.connections.append(connection)

    def get_attributes(self):
        """ returns the attributes as a dict of the Junction

        """
        retdict = {}
        retdict['name'] = self.name
        retdict['id'] = str(self.id)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Junction

        """
        element = ET.Element('junction',attrib=self.get_attributes())
        for con in self.connections:
            element.append(con.get_element())
        return element

#from .exceptions import NotSameAmountOfLanesError
from .enumerations import ContactPoint

def are_roads_consecutive(road1, road2): 
    """ checks if road2 follows road1

        Parameters
        ----------
            road1 (Road): the first road

            road1 (Road): the second road
        Returns
        -------
            bool
    """

    if road1.successor is not None and road2.predecessor is not None: 
        if road1.successor.element_type == ElementType.road and road2.predecessor.element_type == ElementType.road:
            if road1.successor.element_id == road2.id and road2.predecessor.element_id == road1.id: 
                return True 

    return False

def are_roads_connected(road1,road2):
    """ checks if road1 and road2 are connected as successor/successor or predecessor/predecessor

        Parameters
        ----------
            road1 (Road): the first road

            road1 (Road): the second road
        Returns
        -------
            bool, str (successor or predecessor)
    """
    if road1.successor is not None and road2.successor is not None: 
        if road1.successor.element_type == ElementType.road and road2.successor.element_type == ElementType.road:
            if road1.successor.element_id == road2.id and road2.successor.element_id == road1.id: 
                return True, 'successor'
    if road1.predecessor is not None and road2.predecessor is not None: 
        if road1.predecessor.element_type == ElementType.road and road2.predecessor.element_type == ElementType.road:
            if road1.predecessor.element_id == road2.id and road2.predecessor.element_id == road1.id: 
                return True, 'predecessor'
    return False, ''

def create_lane_links(road1,road2):
    """ create_lane_links takes two roads and if they are connected, match their lanes 
        and creates lane links. 
        NOTE: now only works for roads/connecting roads with the same amount of lanes

        Parameters
        ----------
            road1 (Road): first road to be lane linked

            road2 (Road): second road to be lane linked
    """
    if road1.road_type == -1 and road2.road_type == -1:
        #both are roads
        if are_roads_consecutive(road1, road2): 
            _create_links_roads(road1,road2)
        elif are_roads_consecutive(road2, road1): 
            _create_links_roads(road2,road1)
        else:
            connected,connectiontype = are_roads_connected(road1,road2)
            if connected:
                _create_links_roads(road1,road2,connectiontype)
                
    elif road1.road_type != -1:
        _create_links_connecting_road(road1,road2)
    elif road2.road_type != -1:

        _create_links_connecting_road(road2,road1)
    
def _create_links_connecting_road(connecting,road):
    """ _create_links_connecting_road will create lane links between a connecting road and a normal road

        Parameters
        ----------
            connecting (Road): a road of type connecting road (not -1)

            road (Road): a that connects to the connecting road

    """
    linktype, sign, connecting_lanesec =  _get_related_lanesection(connecting,road)
    _, _, road_lanesection_id =  _get_related_lanesection(road,connecting)

    if connecting_lanesec != None:
        if connecting.lanes.lanesections[connecting_lanesec].leftlanes:
            # do left lanes
            for i in range(len(connecting.lanes.lanesections[road_lanesection_id].leftlanes)):
                linkid = road.lanes.lanesections[road_lanesection_id].leftlanes[i].lane_id*sign
                if linktype == 'predecessor':
                    linkid += connecting.lane_offset_pred
                else:
                    linkid += connecting.lane_offset_suc
                connecting.lanes.lanesections[connecting_lanesec].leftlanes[i].add_link(linktype,linkid)
            
        if connecting.lanes.lanesections[connecting_lanesec].rightlanes:
            # do right lanes
            for i in range(len(connecting.lanes.lanesections[connecting_lanesec].rightlanes)):
                linkid = road.lanes.lanesections[road_lanesection_id].rightlanes[i].lane_id*sign
                if linktype == 'predecessor':
                    linkid += connecting.lane_offset_pred
                else:
                    linkid += connecting.lane_offset_suc
                connecting.lanes.lanesections[connecting_lanesec].rightlanes[i].add_link(linktype,linkid)


def _get_related_lanesection(road,connected_road):
    """ _get_related_lanesection takes two roads, and gives the correct lane section to use
        the type of link and if the sign of lanes should be switched

        Parameters
        ----------
            road (Road): the road that you want the information about

            connected_road (Road): the connected road

        Returns
        -------
            linktype (str): the linktype of road to connected road (successor or predecessor)

            sign (int): +1 or -1 depending on if the sign should change in the linking

            road_lanesection_id (int): what lanesection in the road that should be used to link
    """
    linktype = None
    sign = None
    road_lanesection_id = None
 
    if road.successor and road.successor.element_id == connected_road.id:
        linktype = 'successor'
        if road.successor.contact_point == ContactPoint.start:
            sign = 1
        else:
            sign = -1
        road_lanesection_id = -1

    elif road.predecessor and road.predecessor.element_id == connected_road.id:
        linktype = 'predecessor'
        if road.predecessor.contact_point == ContactPoint.start:
            sign = -1
        else:
            sign = 1
        road_lanesection_id = 0

    if connected_road.road_type != -1:
        # treat connecting road in junction differently 
        if connected_road.predecessor.element_id == road.id:
            if connected_road.predecessor.link_type == ContactPoint.start:
                road_lanesection_id = -1
                sign = -1
            else:
                road_lanesection_id = 0
                sign = 1
        elif connected_road.successor.element_id == road.id:
            if connected_road.predecessor.link_type == ContactPoint.start:
                road_lanesection_id = 0
                sign = 1
            else:
                road_lanesection_id = -1
                sign = -1
    return linktype, sign, road_lanesection_id

def _create_links_roads(pre_road,suc_road,same_type=''):
    """ _create_links_roads takes two roads and connect the lanes with links, if they have the same amount. 

        Parameters
        ----------
            pre_road (Road): the predecessor road 

            suc_road (Road): the successor road

            same_type (str): used if the roads are connecting to the same type, predecessor or successor

    """
    if same_type != '':
        if same_type == 'successor':
            lane_sec_pos = -1
        else:
            lane_sec_pos = 0

        if len(pre_road.lanes.lanesections[lane_sec_pos].leftlanes) == len(suc_road.lanes.lanesections[lane_sec_pos].rightlanes):
            for i in range(len(pre_road.lanes.lanesections[lane_sec_pos].leftlanes)):
                linkid = pre_road.lanes.lanesections[lane_sec_pos].leftlanes[i].lane_id
                pre_road.lanes.lanesections[lane_sec_pos].leftlanes[i].add_link(same_type,linkid*-1)
                suc_road.lanes.lanesections[lane_sec_pos].rightlanes[i].add_link(same_type,linkid)
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right and left lanes, to connect as ' +same_type+'/'+same_type)

        if len(pre_road.lanes.lanesections[lane_sec_pos].rightlanes) == len(suc_road.lanes.lanesections[-1].leftlanes):
            for i in range(len(pre_road.lanes.lanesections[lane_sec_pos].rightlanes)):
                linkid = pre_road.lanes.lanesections[lane_sec_pos].rightlanes[i].lane_id
                pre_road.lanes.lanesections[lane_sec_pos].rightlanes[i].add_link(same_type,linkid*-1)
                suc_road.lanes.lanesections[lane_sec_pos].leftlanes[i].add_link(same_type,linkid)
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right and left lanes, to connect as ' +same_type+'/'+same_type)

    else:
        pre_linktype, pre_sign, pre_connecting_lanesec =  _get_related_lanesection(pre_road,suc_road)
        suc_linktype, _, suc_connecting_lanesec =  _get_related_lanesection(suc_road,pre_road)
        if len(pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes) == len(suc_road.lanes.lanesections[-1].leftlanes):
            for i in range(len(pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes)):
                linkid = pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes[i].lane_id*pre_sign
                pre_road.lanes.lanesections[pre_connecting_lanesec].leftlanes[i].add_link(pre_linktype,linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].leftlanes[i].add_link(suc_linktype,linkid*pre_sign)
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right lanes.')


        if len(pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes) == len(suc_road.lanes.lanesections[-1].rightlanes):
            for i in range(len(pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes)):
                linkid = pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes[i].lane_id
                pre_road.lanes.lanesections[pre_connecting_lanesec].rightlanes[i].add_link(pre_linktype,linkid)
                suc_road.lanes.lanesections[suc_connecting_lanesec].rightlanes[i].add_link(suc_linktype,linkid)
        else:
            raise NotSameAmountOfLanesError('Road ' + str(pre_road.id) + ' and road ' + str(suc_road.id) + ' does not have the same number of right lanes.')

class JunctionGroup():
    """ JunctionGroup creates a JunctionGroup of OpenDRIVE
        
        Parameters
        ----------
            name (str): name of the junctiongroup

            group_id (int): id of the junctiongroup

            junction_type (JunctionGroupType): type of junction
                Default: JunctionGroupType.roundabout

        Attributes
        ----------
            name (str): name of the junctiongroup

            group_id (int): id of the junctiongroup

            junctions (list of int): all the junctions in the junctiongroup

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            add_junction(junction_id)
                Adds a connection to the junction
    """

    def __init__(self,name,group_id,junction_type=JunctionGroupType.roundabout):
        """ initalize the JunctionGroup

        Parameters
        ----------
            name (str): name of the junctiongroup

            group_id (int): id of the junctiongroup

            junction_type (JunctionGroupType): type of junction
                Default: JunctionGroupType.roundabout
        """
        self.name = name
        self.group_id = group_id
        self.junctions = []
        self.junction_type = junction_type

    def __eq__(self, other):
        if isinstance(other,JunctionGroup):
            if self.get_attributes() == other.get_attributes() and \
            self.junctions == other.junctions:
                return True
        return False

    def add_junction(self,junction_id):
        """ Adds a new link to the JunctionGroup

            Parameters
            ----------
                junction_id (int): adds a junction to the junctiongroup

        """
        self.junctions.append(junction_id)

    def get_attributes(self):
        """ returns the attributes as a dict of the JunctionGroup

        """
        retdict = {}
        retdict['name'] = self.name
        retdict['id'] = str(self.group_id)
        retdict['type'] = enum2str(self.junction_type)
        return retdict

    def get_element(self):
        """ returns the elementTree of the Junction

        """
        element = ET.Element('junctionGroup',attrib=self.get_attributes())
        for j in self.junctions:
            ET.SubElement(element,'junctionReference',attrib={'junction':str(j)})
        return element
