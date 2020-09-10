import xml.etree.ElementTree as ET

from .helpers import printToFile
from .links import _Link, _Links
from .enumerations import ElementType
import datetime as dt


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
    def adjust_startpoints(self): 
        """ Adjust starting position of all added roads

            Parameters
            ----------

        """
        for road in self.roads:
            if road.road_type != -1: # road is junction 
                for r in self.roads:

                        if road.links.get_predecessor_id() == r.id:
                            #save end position 
                            x,y,h = r.get_end_point()
                            print('predecessor is ', road.links.get_predecessor_id() )
                            print('predecessor cords are ', x, y, h)
                            #adjust current road 
                            road.planview.set_start_point(x,y,h)                            
                            road.planview.adjust_geometires()

                            #if road is junction then try to mirror lanes into predecessor road 
                            if len(road.lanes.lanesections[-1].leftlanes) == len(r.lanes.lanesections[-1].leftlanes) and road.road_type != -1:
                                for i in range(len(road.lanes.lanesections[-1].leftlanes)):
                                    linkid = r.lanes.lanesections[-1].leftlanes[i].lane_id
                                    print('adding link to lane ', linkid)
                                    road.lanes.lanesections[-1].leftlanes[i].add_link('predecessor',linkid)
                            # else:
                            #     raise ValueError('different amount of left lanes')
                            if len(road.lanes.lanesections[-1].rightlanes) == len(r.lanes.lanesections[-1].rightlanes) and road.road_type != -1:
                                for i in range(len(road.lanes.lanesections[-1].rightlanes)):
                                    print('adding link')
                                    linkid = r.lanes.lanesections[-1].rightlanes[i].lane_id
                                    road.lanes.lanesections[-1].rightlanes[i].add_link('predecessor',linkid)
                            # else:
                            #     raise ValueError('different amount of right lanes')
                        elif road.links.get_successor_id() == r.id and road.links.get_successor_type() is not ElementType.junction:
                            x,y,h = road.get_end_point()
                            #adjust next road 
                            print('successor is ', road.links.get_successor_id() )
                            print('junction cords are ', x, y, h)
                            r.planview.set_start_point(x,y,h)
                            r.planview.adjust_geometires()
                            #if road is junction then try to mirror lanes into successor road 
                            if len(road.lanes.lanesections[-1].leftlanes) == len(r.lanes.lanesections[-1].leftlanes) and road.road_type != -1:
                                for i in range(len(road.lanes.lanesections[-1].leftlanes)):
                                    linkid = r.lanes.lanesections[-1].leftlanes[i].lane_id
                                    print('adding link to lane ', linkid)
                                    road.lanes.lanesections[-1].leftlanes[i].add_link('successor',linkid)
                            # else:
                            #     raise ValueError('different amount of left lanes')
                            if len(road.lanes.lanesections[-1].rightlanes) == len(r.lanes.lanesections[-1].rightlanes) and road.road_type != -1:
                                for i in range(len(road.lanes.lanesections[-1].rightlanes)):
                                    linkid = r.lanes.lanesections[-1].rightlanes[i].lane_id
                                    road.lanes.lanesections[-1].rightlanes[i].add_link('successor',linkid)
                            # else:
                            #     raise ValueError('different amount of right lanes')
            else: # normal road   
                for r in self.roads:        
                    if road.links.get_predecessor_id() == r.id and road.links.get_predecessor_type() is not ElementType.junction:
                        print('am i here')
                        x,y,h = r.get_end_point()
                        road.planview.set_start_point(x,y,h)
                        road.planview.adjust_geometires()

                        #try to link lanes
                        if len(road.lanes.lanesections[-1].leftlanes) == len(r.lanes.lanesections[-1].leftlanes):
                            for i in range(len(road.lanes.lanesections[-1].leftlanes)):
                                linkid = road.lanes.lanesections[-1].leftlanes[i].lane_id
                                road.lanes.lanesections[-1].leftlanes[i].add_link('predecessor',linkid)
                                r.lanes.lanesections[0].leftlanes[i].add_link('successor',linkid)
                        # else:
                        #     raise ValueError('different amount of left lanes')

                        if len(road.lanes.lanesections[-1].rightlanes) == len(r.lanes.lanesections[-1].rightlanes):
                            for i in range(len(road.lanes.lanesections[-1].rightlanes)):
                                linkid = road.lanes.lanesections[-1].rightlanes[i].lane_id
                                road.lanes.lanesections[-1].rightlanes[i].add_link('predecessor',linkid)
                                r.lanes.lanesections[0].rightlanes[i].add_link('successor',linkid)
                                break
                        # else:
                        #     raise ValueError('different amount of right lanes')
                    elif road.links.get_predecessor_id() == r.id and road.links.get_predecessor_type() is ElementType.junction:
                        break
                    elif len(road.planview._adjusted_geometries) == 0:
                        road.planview.adjust_geometires()
                        break

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
        