import xml.etree.ElementTree as ET
from .helpers import enum2str



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

    def add_link(self,link):
        """ Adds a _Link 

            Parameters
            ----------
                link (_Link): a link to be added to the Links

        """
        self.links.append(link)

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

    def get_attributes(self):
        """ returns the attributes as a dict of the _Link

        """
        retdict = {}
        if self.element_type == None:
            retdict['Id'] = self.element_id
        else:
            retdict['elementType'] = enum2str(self.element_type)
            retdict['elementId'] = self.element_id
        
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


class Connection():
    """ Connection creates a connection as a base of junction
        
        Parameters
        ----------
            incoming_road (int): the id of the incoming road to the junciton

            connecting_road (int): id of the connecting road (type junction)
            
            contact_point (ContactPoint): the contact point of the link

            id (int): id of the junction (automated?)

        Attributes
        ----------
            incoming_road (int): the id of the incoming road to the junciton

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
            incoming_road (int): the id of the incoming road to the junciton

            connecting_road (int): id of the connecting road (type junction)
            
            contact_point (ContactPoint): the contact point of the link

            id (int): id of the junction (automated)
        """

        self.incoming_road = incoming_road
        self.connecting_road = connecting_road
        self.contact_point = contact_point
        self.id = id
        self.links = []

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


