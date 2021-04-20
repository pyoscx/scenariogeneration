""" This is a collection of ready to use functions, to generate standard road snipets, like:
    - Simple straight road
    - Spiral-Arc-Spiral type of turns
    - Simple roads with different geometries and lanes
    - Simple junction roads
        limited to 3/4-way crossings with 90degree turns (3-way can be 120 deg aswell)
    - Creation of the junction based on the connecting roads and incomming/outgoing roads
"""
import numpy as np

from .lane import Lane, RoadMark, LaneSection, Lanes
from .enumerations import RoadMarkType, MarkRule, ContactPoint, ElementType, ObjectType

from .geometry import Line, Arc, Spiral, EulerSpiral, PlanView
from .opendrive import Road, OpenDrive
from .links import Junction, Connection, _get_related_lanesection


STD_ROADMARK_SOLID = RoadMark(RoadMarkType.solid,0.2)
STD_ROADMARK_BROKEN = RoadMark(RoadMarkType.broken,0.2)
STD_START_CLOTH = 1/1000000000
def standard_lane(offset=3,rm = STD_ROADMARK_BROKEN):
    """ standard_lane creates a simple lane with an offset an a roadmark
        
        Parameters
        ----------
            offset (int): width of the lane
                default: 3

            rm (RoadMark): road mark used for the standard lane
                default:  RoadMark(STD_ROADMARK_BROKEN)
        Returns
        -------
            lane (Lane): the lane

    """
    lc = Lane(a=offset)
    lc.add_roadmark(rm)
    return lc


def create_road(geometry,id,left_lanes = 1, right_lanes = 1,road_type=-1,center_road_mark = STD_ROADMARK_SOLID, lane_width=3):
    """ create_road creates a road with one lanesection with different number of lanes, lane marks will be of type broken, 
        except the outer lane, that will be solid. 

        Parameters
        ----------
            geometry (Line, Spiral, ParamPoly3, or Arc, or list with these): geometries to build the road

            id (int): id of the new road

            left_lanes (int): number of left lanes wanted
                Default: 1

            right_lanes (int): number of right lanes wanted
                Default: 1

            road_type (int): type of road, -1 normal road, otherwise connecting road

            center_road_mark (RoadMark): roadmark for the center line

            lane_width (float): the with of all lanes
    
        Returns
        -------
            road (Road): a straight road
    """
    pv = PlanView()
    raw_length = 0
    if isinstance(geometry,list):
        for g in geometry:
            pv.add_geometry(g)
            raw_length += g.length
    else:
        pv.add_geometry(geometry)
        raw_length += geometry.length
    
    # create centerlane
    lc = Lane(a=0)
    lc.add_roadmark(center_road_mark)

    lsec = LaneSection(0,lc)
    # create left lanes
    for i in range(left_lanes):
        if i == left_lanes-1:
            leftlane = standard_lane(lane_width,STD_ROADMARK_SOLID) 
        else:
            leftlane = standard_lane(lane_width,STD_ROADMARK_BROKEN) 
        lsec.add_left_lane(leftlane)
    
    for i in range(right_lanes):
        if i == right_lanes-1:
            rightlane = standard_lane(lane_width,STD_ROADMARK_SOLID)
        else:
            rightlane = standard_lane(lane_width,STD_ROADMARK_BROKEN)
        lsec.add_right_lane(rightlane)
    lanes = Lanes()
    lanes.add_lanesection(lsec)
    
    road = Road(id,pv,lanes,road_type=road_type)
    
    return road

def create_straight_road(road_id, length=100,junction = -1, n_lanes=1, lane_offset=3):
    """ creates a standard straight road with two lanes

        Parameters
        ----------
            road_id (int): id of the road to create

            length (float): length of the road
                default: 100

            junction (int): if the road belongs to a junction or not
                default: -1
        Returns
        -------
            road (Road): a straight road
    """
    # create geometry
    line1 = Line(length)

    # create planviews
    planview1 = PlanView()
    planview1.add_geometry(line1)

    # create lanesections
    lanesec1 = LaneSection(0,standard_lane())
    for i in range(1, n_lanes+1, 1):
        lanesec1.add_right_lane(standard_lane(lane_offset))
        lanesec1.add_left_lane(standard_lane(lane_offset))

    # create lanes
    lanes1 = Lanes()
    lanes1.add_lanesection(lanesec1)

    # finally create the roads 
    return Road(road_id,planview1,lanes1,road_type=junction)


def create_cloth_arc_cloth(arc_curv, arc_angle, cloth_angle, r_id, junction = 1,cloth_start = STD_START_CLOTH, n_lanes=1, lane_offset=3):
    """ creates a curved Road  with a Spiral - Arc - Spiral, and two lanes

        Parameters
        ----------
            arc_curv (float): curvature of the arc (and max clothoid of clothoids)

            arc_angle (float): how much of the curv should be the arc

            cloth_angle (float): how much of the curv should be the clothoid (will be doubled since there are two clothoids)
            
            r_id (int): the id of the road

            junction (int): if the Road belongs to a junction
                default: 1

            cloth_start (float): staring curvature of clothoids

        Returns
        -------
            road (Road): a road built up of a Spiral-Arc-Spiral
    """
    
    pv = PlanView()
    # adjust sign if angle is negative
    if cloth_angle < 0 and  arc_curv > 0:

        cloth_angle = -cloth_angle
        arc_curv = -arc_curv
        cloth_start = -cloth_start
        arc_angle = -arc_angle 
    
    # create geometries
    spiral1 = Spiral(cloth_start, arc_curv, angle=cloth_angle)
    arc = Arc(arc_curv, angle=arc_angle )
    spiral2 = Spiral(arc_curv, cloth_start, angle=cloth_angle)

    pv.add_geometry(spiral1)
    pv.add_geometry(arc)
    pv.add_geometry(spiral2)

    # create lanes
    lsec = LaneSection(0,standard_lane())
    for i in range(1, n_lanes+1, 1):
        lsec.add_right_lane(standard_lane(lane_offset))
        lsec.add_left_lane(standard_lane(lane_offset))
    lanes = Lanes()
    lanes.add_lanesection(lsec)

    # create road
    return Road(r_id,pv,lanes,road_type=junction)

def get_lanes_offset(road1, road2, contactpoint):
    """ returns number of lanes (hp #left lanes = # right lanes) and their offset (hp offset is constant)


        Parameters
        ----------
            road1 (Road): first road 

            road2 (Road): second road 

        Returns
        -------
            n_lanes (int): 

            lane_offset (int):
    """
    #now we always look at lanesection[0] to take the number of lanes 
    #TO DO - understand if the roads are connect through end or start and then take the relative lane section 
    if contactpoint == ContactPoint.end: 
        n_lanesection = 0 
    else:
        n_lanesection = -1
    if len(road1.lanes.lanesections[n_lanesection].leftlanes) == len(road2.lanes.lanesections[0].leftlanes) and len(road1.lanes.lanesections[n_lanesection].rightlanes) == len(road2.lanes.lanesections[0].rightlanes):
        n_lanes = len(road1.lanes.lanesections[n_lanesection].leftlanes) 
        lane_offset = road1.lanes.lanesections[n_lanesection].leftlanes[0].a     
    else:
        raise NotSameAmountOfLanesError('Incoming road ',road1.id, ' and outcoming road ', road2.id, 'do not have the same number of left lanes.')
        
    return n_lanes, lane_offset 




def create_junction_roads_standalone(angles,r,junction=1,spiral_part = 1/3, arc_part = 1/3,startnum=100,n_lanes=1,lane_width=3):
    """ creates all needed roads for some simple junctions, the curved parts of the junction are created as a spiral-arc-spiral combo 
        - 3way crossings (either a T junction, or 120 deg junction)
        - 4way crossing (all 90 degree turns)
        NOTE: this will not generate any links or add any successor/predecessors to the roads, and has to be added manually,
        if you have the connecting roads please use create_junction_roads

        Parameters
        ----------
       
            angles (list of float): the angles which the roads should be going out (see description for what is supported), 
                                    should be defined mathimatically positive (incoming road 0)

            r (float): the radius of the arcs in the junction (will determine the size of the junction)
            
            junction (int): the id of the junction
                default: 1

            spiral_part (float): the part of the curve that should be spirals (two of these) spiral_part*2 + arcpart = angle of the turn
                default: (1/3)

            arc_part (float): the part of the curve that should be an arc:  spiral_part*2 + arcpart = angle of the turn
                default: (1/3)

            startnum (int): start number of the roads in the junctions (will increase with 1 for each road)
            
            n_lanes (int): the number of lanes in the junction

            lane_width (double): the lane width of the lanes in the junction
        Returns
        -------
            junction_roads (list of Road): a list of all roads in a junction without connections added

    """
    angle = np.pi/2
    angle_cloth = angle*spiral_part 
    spiral_length = 2*abs(angle_cloth*r)

    spiral = EulerSpiral.createFromLengthAndCurvature(spiral_length, STD_START_CLOTH, 1/r)
    (X, Y, _) = spiral.calc(spiral_length, 0, 0, STD_START_CLOTH, 0)

    X0 = X-r*np.sin(angle_cloth)
    Y0 = Y-r*(1-np.cos(angle_cloth))
    linelength = 2*(X0 + r + Y0)

    junction_roads = []
    
    for i in range(len(angles)-1):
        
        for j in range(1+i,len(angles)):
            # check angle needed for junction
            an = np.sign(angles[j]-angles[i]-np.pi)
            an1 = angles[j]-angles[i] -np.pi
            angle_arc = an1*arc_part

            angle_cloth = an1*spiral_part

            #adjust angle if multiple of pi
            if an1 > np.pi: 
                an1 = -(2*np.pi - an1)

            # create road, either straight or curved
            if an == 0:
                tmp_junc = create_straight_road(startnum,length= linelength,junction=junction, n_lanes=n_lanes, lane_offset=lane_width)
            else: 
                tmp_junc = create_cloth_arc_cloth(  1/r , angle_arc , angle_cloth , startnum , junction, n_lanes=n_lanes, lane_offset=lane_width )

            # add predecessor and successor
            startnum += 1
            junction_roads.append(tmp_junc)

    return junction_roads
    
def create_junction_roads(roads,angles,r,junction=1,spiral_part = 1/3, arc_part = 1/3,startnum=100):
    """ creates all needed roads for some simple junctions, the curved parts of the junction are created as a spiral-arc-spiral combo
        Supported junctions:
        - 3way crossings (either a T junction, or 120 deg junction)
        - 4way crossing (all 90 degree turns)

        Parameters
        ----------
            roads (list of Road): all roads that should go into the junction

            angles (list of float): the angles which the roads should be going out (see description for what is supported), 
                                    should be defined mathimatically positive (incoming road 0)

            r (float): the radius of the arcs in the junction (will determine the size of the junction)
            
            junction (int): the id of the junction
                default: 1

            spiral_part (float): the part of the curve that should be spirals (two of these) spiral_part*2 + arcpart = angle of the turn
                default: (1/3)

            arc_part (float): the part of the curve that should be an arc:  spiral_part*2 + arcpart = angle of the turn
                default: (1/3)

            startnum (int): start number of the roads in the junctions (will increase with 1 for each road)

        Returns
        -------
            junction_roads (list of Road): a list of all roads needed for all traffic connecting the roads
    """

    # if a straight line is used, calculate the length of it. Some Spiral Magic going on...
    # http://www.jerrymahun.com/index.php/home/open-access/viii-curves/76-chapter-e-spirals?showall=1

    angle = np.pi/2
    angle_cloth = angle*spiral_part 
    spiral_length = 2*abs(angle_cloth*r)

    spiral = EulerSpiral.createFromLengthAndCurvature(spiral_length, STD_START_CLOTH, 1/r)
    (X, Y, _) = spiral.calc(spiral_length, 0, 0, STD_START_CLOTH, 0)

    X0 = X-r*np.sin(angle_cloth)
    Y0 = Y-r*(1-np.cos(angle_cloth))
    linelength = 2*(X0 + r + Y0)

    junction_roads = []

    # loop over the roads to get all possible combinations of connecting roads
    for i in range(len(roads)-1):
        # for now the first road is place as base, 
        if i == 0:
            cp = ContactPoint.end
            roads[i].add_successor(ElementType.junction,junction)
        else:
            cp = ContactPoint.start
            roads[i].add_predecessor(ElementType.junction,junction)
        
        for j in range(1+i,len(roads)):
            # check angle needed for junction
            an = np.sign(angles[j]-angles[i]-np.pi)
            an1 = angles[j]-angles[i] -np.pi
            angle_arc = an1*arc_part

            angle_cloth = an1*spiral_part

            #adjust angle if multiple of pi
            if an1 > np.pi: 
                an1 = -(2*np.pi - an1)

            # create road, either straight or curved
            n_lanes, lanes_offset = get_lanes_offset(roads[i], roads[j], cp )
            if an == 0:
                tmp_junc = create_straight_road(startnum,length= linelength,junction=junction, n_lanes=n_lanes, lane_offset=lanes_offset)
            else: 
                tmp_junc = create_cloth_arc_cloth(  1/r , angle_arc , angle_cloth , startnum , junction, n_lanes=n_lanes, lane_offset=lanes_offset )

            # add predecessor and successor
            tmp_junc.add_predecessor(ElementType.road,roads[i].id,cp)
            tmp_junc.add_successor(ElementType.road,roads[j].id,ContactPoint.start)
            startnum += 1
            junction_roads.append(tmp_junc)

    # add junction to the last road aswell since it's not part of the loop
    roads[-1].add_predecessor(ElementType.junction,junction)

    return junction_roads

def _create_junction_links(connection, nlanes,r_or_l,sign,from_offset=0,to_offset=0):
    """ helper function to create junction links

        Parameters
        ----------
            connection (Connection): the connection to fill

            nlanes (int): number of lanes 

            r_or_l (1 or -1): if the lane should start from -1 or 1

            sign (1 or -1): if the sign should change 

            from_offset (int): if there is an offset in the beginning 
                Default: 0

            to_offset (int): if there is an offset in the end of the road 
                Default: 0
    """
    for i in range(1, nlanes+1, 1):
        connection.add_lanelink( r_or_l*i+from_offset, r_or_l*sign*i+to_offset)


def create_junction(junction_roads, id, roads, name='my junction'):
    """ create_junction creates the junction struct for a set of roads


        Parameters
        ----------
            junction_roads (list of Road): all connecting roads in the junction

            id (int): the id of the junction
            
            roads (list of Road): all incomming roads to the junction
            
            name(str): name of the junction
            default: 'my junction'

        Returns
        -------
            junction (Junction): the junction struct ready to use

    """



    junc = Junction(name,id)
    
    for jr in junction_roads:
        # handle succesor lanes
        conne1 = Connection(jr.successor.element_id,jr.id,ContactPoint.end) 
        _, sign, _ =  _get_related_lanesection(jr,get_road_by_id(roads,jr.successor.element_id) ) 

        _create_junction_links(conne1,len(jr.lanes.lanesections[-1].rightlanes),-1,sign,to_offset=jr.lane_offset_suc)
        _create_junction_links(conne1,len(jr.lanes.lanesections[-1].leftlanes),1,sign,to_offset=jr.lane_offset_suc)
        junc.add_connection(conne1)

        # handle predecessor lanes
        conne2 = Connection(jr.predecessor.element_id,jr.id,ContactPoint.start)
        _, sign, _ =  _get_related_lanesection( jr,get_road_by_id(roads,jr.predecessor.element_id)) 
        _create_junction_links(conne2,len(jr.lanes.lanesections[0].rightlanes),-1,sign,from_offset=jr.lane_offset_pred)
        _create_junction_links(conne2,len(jr.lanes.lanesections[0].leftlanes),1,sign,from_offset=jr.lane_offset_pred)
        junc.add_connection(conne2)
    return junc

def get_road_by_id(roads,id):
    """ get_road_by_id returns a road based on the road id

        Parameters
        ----------
            roads (list of Roads): a list of roads to seach through

            id (int): the id of the road wanted

        Returns
        -------
            Road
    """
    for r in roads:
        if r.id == id:
            return r