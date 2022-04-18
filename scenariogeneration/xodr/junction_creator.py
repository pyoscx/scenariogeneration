

from os import link
from tracemalloc import start
from .enumerations import JunctionType, ElementType, ContactPoint
from .geometry import Spiral, Line
from .generators import create_road, _get_related_lanesection
from .links import Junction, Connection
import pyclothoids as pcloth

import numpy as np
STD_START_CLOTH = 1 / 1000000000

class JunctionCreator():
    

    def __init__(self, id, name, junction_type = JunctionType.default, startnum = 100):
        self.id = id
        self.junction_type = junction_type
        self.incomming_roads = []
        self._radie = []
        self._angles = []
        self._x = []
        self._y = []
        self._h = []
        self.junction_roads = []
        self.startnum = startnum
        self.junction = Junction(name, id)
        self._circular_junction = False
        self._generic_junction = False

    def add_incomming_road_circular_junction(self, road, radius, angle):
        self.incomming_roads.append(road)
        self._radie.append(radius)
        self._angles.append(angle)
        self._circular_junction = True

    def add_incomming_road_generic_junction(self, road, x, y, heading):

        self.incomming_roads.append(road)
        self._x.append(x)
        self._y.append(y)
        self._h.append(heading)
        self._generic_junction = True

    def generate_junction_roads(self):
        pass
    
    def _get_list_index(self, id):        
        return [self.incomming_roads.index(x) for x in self.incomming_roads if x.id == id][0]

    def _get_contact_point_connecting_road(self, road_id):
        incomming_road = self.incomming_roads[self._get_list_index(road_id)]
        if incomming_road.successor and incomming_road.successor.element_id == self.id:
            return ContactPoint.end
        elif incomming_road.predecessor and incomming_road.predecessor.element_id == self.id:
            return ContactPoint.start
        else:
            raise AttributeError('road is not connected to this junction')
    
    def _get_connecting_lane_section(self, idx):
        incomming_road = self.incomming_roads[idx]
        if incomming_road.successor and incomming_road.successor.element_id == self.id:
            return -1
        elif incomming_road.predecessor and incomming_road.predecessor.element_id == self.id:
            return 0
        else:
            raise AttributeError('road is not connected to this junction')
    
    def add_connection(self, road_one_id, road_two_id, lane_one_id=None, lane_two_id=None):
        
        if (lane_one_id == None) and (lane_two_id == None):
            #TODO: check that number of lanes are the same
            self._create_connecting_roads_with_equal_lanes(road_one_id, road_two_id)
    
    def _create_connecting_roads_with_equal_lanes(self, road_one_id, road_two_id):
        idx1 = self._get_list_index(road_one_id)
        idx2 = self._get_list_index(road_two_id)
        
        # check if the road has _angles/radius for these roads
        if self._circular_junction:
            roadgeoms = self._create_road_circular_geometry(idx1, idx2)
        elif self._generic_junction:
            roadgeoms = self._create_generic_geometry(idx1, idx2)

        
        tmp_junc_road = create_road(roadgeoms,
        self.startnum,
        left_lanes=len(self.incomming_roads[idx1].lanes.lanesections[self._get_connecting_lane_section(idx1)].leftlanes),
        right_lanes=len(self.incomming_roads[idx1].lanes.lanesections[self._get_connecting_lane_section(idx1)].rightlanes), 
        lane_width=self.incomming_roads[idx1].lanes.lanesections[self._get_connecting_lane_section(idx1)].leftlanes[0].a,
        road_type=self.id)

        tmp_junc_road.add_predecessor(ElementType.road, road_one_id, contact_point=self._get_contact_point_connecting_road(road_one_id))
        tmp_junc_road.add_successor(ElementType.road, road_two_id, contact_point=self._get_contact_point_connecting_road(road_two_id))
        self.junction_roads.append(tmp_junc_road)
        self.startnum += 1



    def _create_generic_geometry(self, idx1, idx2):
        an1 = self._h[idx2] - self._h[idx1] - np.pi
        # adjust angle if multiple of pi
        if an1 > np.pi:
            an1 = -(2 * np.pi - an1)

        if np.sign(an1) == 0:
            roadgeoms = Line(np.sqrt((self._x[idx2]-self._x[idx1] )**2 + (self._y[idx2]-self._y[idx1] )**2 ))
        else:
            
            clothoids = pcloth.SolveG2(
                    0,
                    0,
                    self._h[idx1] - np.pi,
                    STD_START_CLOTH,
                    self._x[idx2] - self._x[idx1],
                    self._y[idx2] - self._y[idx1],
                    self._h[idx2],
                    STD_START_CLOTH,
                )
            roadgeoms = [Spiral(x.KappaStart, x.KappaEnd, length=x.length) for x in clothoids]
        return roadgeoms

    def _create_road_circular_geometry(self, idx1, idx2):

        an1 = self._angles[idx2] - self._angles[idx1] - np.pi
        # adjust angle if multiple of pi
        if an1 > np.pi:
            an1 = -(2 * np.pi - an1)

        if np.sign(an1) == 0:
            roadgeoms = Line(self._radie[idx1] +self._radie[idx2] )
        else:
            clothoids = pcloth.SolveG2(
                    -self._radie[idx1],
                    0,
                    0,
                    STD_START_CLOTH,
                    self._radie[idx2] * np.cos(an1),
                    self._radie[idx2] * np.sin(an1),
                    an1,
                    STD_START_CLOTH,
                )
            roadgeoms = [Spiral(x.KappaStart, x.KappaEnd, length=x.length) for x in clothoids]



        return roadgeoms

    def get_connecting_roads(self):
        return self.junction_roads




class DirectJunctionCreator():

    def __init__(self, id, name):
        self.id = id
        self.junction = Junction(name, id, JunctionType.direct)
        

        

    def _get_contact_point_linked_road(self, incomming_road):
        if incomming_road.successor and incomming_road.successor.element_id == self.id:
            return ContactPoint.end
        elif incomming_road.predecessor and incomming_road.predecessor.element_id == self.id:
            return ContactPoint.start
        else:
            raise AttributeError('road is not connected to this junction')

    def add_connection(self,incomming_road, linked_road, incomming_lanes = None, linked_lanes = None, all_roads = None):
        single_road = False
        succ_lane_offset = 0
        pred_lane_offset = 0
        if not isinstance(incomming_lanes,list):
            incomming_lanes = [incomming_lanes]
            single_road = True
        if not isinstance(linked_lanes,list):
            linked_lanes = [linked_lanes]
            single_road = True
        if single_road:
            if abs(incomming_lanes[0]) != abs(linked_lanes[0]):
                lane_offset = abs(incomming_lanes[0]) - abs(linked_lanes[0])
                succ_lane_offset = -1* np.sign(incomming_lanes[0])*lane_offset
                pred_lane_offset = np.sign(linked_lanes[0])*lane_offset
        incomming_road.succ_direct_junction[linked_road.id] =  succ_lane_offset
        linked_road.pred_direct_junction[incomming_road.id] = pred_lane_offset
        if incomming_lanes == None and linked_lanes == None:
            pass
        else:
            connection = Connection(incomming_road.id, linked_road.id, self._get_contact_point_linked_road(linked_road))
            for i in range(len(incomming_lanes)):
                connection.add_lanelink(incomming_lanes[i], linked_lanes[i])
            self.junction.add_connection(connection)