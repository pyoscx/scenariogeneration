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

            element_type (ElementType): type of element the linked road

            element_id (str): name of the linked road

            contact_point (ContactPoint): the contact point of the link

            direction (Direction): the direction of the link (used for neighbor)

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

            element_type (ElementType): type of element the linked road

            element_id (str): name of the linked road

            contact_point (ContactPoint): the contact point of the link

            direction (Direction): the direction of the link (used for neighbor)
        """

        if link_type in ['successor', 'predecessor']:
            if contact_point == None and element_type != None:
                raise ValueError('contact_point has to be defined for successor and predecessor')
        elif link_type == 'neighbor':
            if direction == None:
                raise ValueError('direction has to be defined for neighbor')
        else:
            raise ValueError('unknown input ' + link_type + ', use: successor, predecessor, or neighbor')
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
        
        if self.link_type in ['successor', 'predecessor'] and self.element_type != None:
            
            retdict['contactPoint'] = enum2str(self.contact_point)
        elif self.link_type == 'neighbor':
            retdict['direction'] = enum2str(self.direction)
        return retdict

    def get_element(self):
        """ returns the elementTree of the _Link

        """
        element = ET.Element(self.link_type,attrib=self.get_attributes())
        return element

