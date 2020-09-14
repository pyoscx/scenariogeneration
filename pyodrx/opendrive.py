import xml.etree.ElementTree as ET

from .helpers import printToFile
from .links import _Link, _Links, create_lane_links
from .enumerations import ElementType, ContactPoint

import datetime as dt
import warnings

class _Header():
    """ Header creates the header of the OpenDrive file
        
        Parameters
        ----------
            name (str): name of the road 

        Attributes
        ----------
            name (str): name of the scenario 

        Methods
        -------
            get_element()
                Returns the full ElementTree of FileHeader

            get_attributes()
                Returns a dictionary of all attributes of FileHeader

    """
    def __init__(self,name):
        """ Initalize the Header

         Parameters
        ----------
            name (str): name of the road 
        """
        self.name = name

        

    def get_attributes(self):
        """ returns the attributes as a dict of the FileHeader

        """
        retdict = {}
        retdict['name'] = self.name
        retdict['revMajor'] ='1'
        retdict['revMinor'] ='5'
        retdict['date'] = str(dt.datetime.now())
        retdict['north'] = '0.0'
        retdict['south'] = '0.0'
        retdict['east'] = '0.0'
        retdict['west'] = '0.0'
        return retdict

    def get_element(self):
        """ returns the elementTree of the FileHeader

        """
        element = ET.Element('header',attrib=self.get_attributes())

        return element


class Road():
    """ Road defines the road element of OpenDrive
        
        Parameters
        ----------
            road_id (int): identifier of the road

            planview (PlanView): the planview of the road

            lanes (Lanes): the lanes of the road

            road_type (int): type of road (junction)
                Default: -1

            name (str): name of the road (optional)

            rule (TrafficRule): traffic rule (optional)

        Attributes
        ----------
            id (int): identifier of the road

            planview (PlanView): the planview of the road

            lanes (Lanes): the lanes of the road

            road_type (int): type of road (junction)
                Default: -1

            name (str): name of the road (optional)

            rule (TrafficRule): traffic rule (optional)

        Methods
        -------
            get_element()
                Returns the full ElementTree of the class

            get_attributes()
                Returns a dictionary of all attributes of the class

            write_xml(filename)
                write a open scenario xml
                
    """
    def __init__(self,road_id,planview,lanes, road_type = -1,name=None, rule=None):
        """ initalize the Road

            Parameters
            ----------
                road_id (int): identifier of the road

                planview (PlanView): the planview of the road

                lanes (Lanes): the lanes of the road

                road_type (int): type of road (junction)
                    Default: -1

                name (str): name of the road (optional)

                rule (TrafficRule): traffic rule (optional)

        """
        self.id = road_id
        self.planview = planview
        self.lanes = lanes
        self.road_type = road_type
        self.name = name
        self.rule = rule
        self.links = _Links()
        self._neighbor_added = 0
        self.successor = None
        self.predecessor = None
    def add_successor(self,element_type,element_id,contact_point=None):
        """ add_successor adds a successor link to the road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the link

        """
        if self.successor:
            raise ValueError('only one successor is allowed')
        self.successor = _Link('successor',element_id,element_type,contact_point)
        self.links.add_link(self.successor)


    def add_predecessor(self,element_type,element_id,contact_point=None):
        """ add_successor adds a successor link to the road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            contact_point (ContactPoint): the contact point of the link

        """
        if self.predecessor:
            raise ValueError('only one predecessor is allowed')
        self.predecessor = _Link('predecessor',element_id,element_type,contact_point)
        self.links.add_link(self.predecessor)
        

    def add_neighbor(self,element_type,element_id,direction): 
        """ add_neighbor adds a neighbor to a road
        
        Parameters
        ----------
            element_type (ElementType): type of element the linked road

            element_id (str/int): name of the linked road

            direction (Direction): the direction of the link 
        """
        if self._neighbor_added > 1:
            raise ValueError('only two neighbors are allowed')
        suc = _Link('neighbor',element_id,element_type,direction=direction)
    
        self.links.add_link(suc)
        self._neighbor_added += 1
    def get_end_point(self):
        """ get the x, y, and heading, of the end of the road

            Return
            ------
                x (float): the end x coordinate
                y (float): the end y coordinate
                h (float): the end heading

        """
        return self.planview.present_x, self.planview.present_y, self.planview.present_h
    def get_attributes(self):
        """ returns the attributes as a dict of the Road

        """
        retdict = {}
        if self.name:
            retdict['name'] = self.name
        if self.rule:
            retdict['rule'] = self.rule
        retdict['id'] = str(self.id)
        retdict['junction'] = str(self.road_type)
        retdict['length'] = str(self.planview.get_total_length())
        return retdict

    def get_element(self):
        """ returns the elementTree of the FileHeader

        """
        element = ET.Element('road',attrib=self.get_attributes())
        element.append(self.links.get_element())
        element.append(self.planview.get_element())
        element.append(self.lanes.get_element())
        
        return element

class OpenDrive():
    """ OpenDrive is the main class of the pyodrx to generate an OpenDrive road
        
        Parameters
        ----------
            name (str): name of the road

        Attributes
        ----------
            name (str): name of the road

            roads (list of Road): all roads 

            junctions (list of Junction): all junctions

        Methods
        -------
            get_element()
                Returns the full ElementTree of FileHeader

            add_road(road)
                Adds a road to the opendrive

            add_junction(junction)
                Adds a junction to the opendrive

            write_xml(filename)
                write a open scenario xml
                
    """
    def __init__(self,name):
        """ Initalize the Header

            Parameters
            ----------
            name (str): name of the road 

        """
        self.name = name
        self._header = _Header(self.name)
        self.roads = []
        self.junctions = []

    def add_road(self,road):
        """ Adds a new road to the opendrive

            Parameters
            ----------
                road (Road): the road to add 

        """
        if (len(self.roads) == 0) and road.predecessor:
            ValueError('No road was added and the added road has a predecessor, please add the predecessor first')

        self.roads.append(road)

    def adjust_roads_and_lanes(self, base_road): 
        self.adjust_startpoints_recursive(base_road, initial=True)

        # create lane links (if possible)
        for i in range(len(self.roads)-1):
            for j in range(i+1,len(self.roads)):
                create_lane_links(self.roads[i],self.roads[j])  


    def adjust_startpoints_recursive(self, base_road, initial=True): 
        """ Adjust starting position of all added roads

            Parameters
            ----------
            base_road (Road): the road where we adjust all other geometries from

        """
        #print('Calling recursive function on road ', base_road.id)

        if base_road.road_type != -1 and initial:
            raise ValueError('We cannot use a junction road as base road to adjust the other geometries')

        if base_road.links.get_predecessor_type() != None and initial:
            warnings.simplefilter("The base road has a predecessor! The geometries of the previous roads will not be added")


        # add geometry of base road 
        if initial: 
            #print('adjusting base road ', base_road.id)
            base_road.planview.adjust_geometires()


        next_road_id = base_road.links.get_successor_id()
        next_road_type = base_road.links.get_successor_type()


        # adjust and add geometry of next normal road 
        if next_road_type is ElementType.road: 
            #print('i am in normal case and next road is ', next_road_id)
            # adjust the next road starting point 
            for r in self.roads:     
                if r.id == next_road_id:
                    #print('found next road with id ', next_road_id)
                    if base_road.links.get_successor_contact_point() is ContactPoint.start or base_road.links.get_successor_contact_point() is None:
                        #print('contact point is start ')
                        x,y,h = base_road.get_end_point()
                        r.planview.set_start_point(x,y,h)
                        #print('adjusting road ', r.id)
                        r.planview.adjust_geometires()

                    elif base_road.links.get_successor_contact_point() is ContactPoint.end:
                        #print('contact point is end ')
                        x,y,h = base_road.get_end_point()
                        r.planview.set_start_point(x,y,h)
                        #print('adjusting road ', r.id)
                        r.planview.adjust_geometires(True)

                    #try to link lanes 
                    self.adjust_startpoints_recursive(r, False)
                    break 
        # if next road is junction I look for the next road, adjust its geometry, add its geometry and go to the next road
        elif next_road_type is ElementType.junction:
            #print('i am in junction case')
            for j in self.junctions: 
                if j.id == next_road_id:
                    for c in j.connections:
                        if c.incoming_road == base_road.id:
                            next_road_id = c.connecting_road
                            #print('found a successor road in connection level ', next_road_id)
                            for r in self.roads:
                                if r.id == next_road_id:
                                    #print('found next road ', r.id)
                                    x,y,h = base_road.get_end_point()
                                    r.planview.set_start_point(x,y,h)
                                    #print('adjusting road ', r.id)
                                    r.planview.adjust_geometires()
                                    self.adjust_startpoints_recursive(r, False)
                                    break
                            
                    break
        elif next_road_id is None:
            print('road does not have any successor ' )

    def add_junction(self,junction):
        """ Adds a junction to the opendrive

            Parameters
            ----------
                junction (Junction): the junction to add

        """
        self.junctions.append(junction)

    def get_element(self):
        """ returns the elementTree of the FileHeader

        """
        element = ET.Element('OpenDRIVE')
        element.append(self._header.get_element())
        for r in self.roads:
            element.append(r.get_element())
    
        for j in self.junctions:
            element.append(j.get_element())

        return element


    def write_xml(self,filename=None,prettyprint = True):
        """ writeXml writes the open scenario xml file

        Parameters
        ----------
            filename (str): path and filename of the wanted xml file
                Default: name of the opendrive

            prettyprint (bool): pretty print or ugly print?
                Default: True

        """
        if filename == None:
            filename = self.name + '.xodr'
        printToFile(self.get_element(),filename,prettyprint)
        