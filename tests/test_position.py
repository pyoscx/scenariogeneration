
import pytest

import pyoscx as OSC

def test_worldposition_noinput():
    pos = OSC.WorldPosition()
    pos.get_attributes()
    p = pos.get_element()
    OSC.prettyprint(p)

def test_worldposition_input():
    pos = OSC.WorldPosition(x=1,y=2,z=1.123)
    pos.get_attributes()
    p = pos.get_element()
    OSC.prettyprint(p)


def test_relativeworldposition():
    
    pos = OSC.RelativeWorldPosition('Ego',1,2,0)
    OSC.prettyprint(pos.get_element())

    pos = OSC.RelativeWorldPosition('Target',1,2,0,orientation=OSC.Orientation(h=0.2))
    OSC.prettyprint(pos.get_element())


def test_relativeobjectposition():
    
    pos = OSC.RelativeObjectPosition('Ego',1,2,0)
    OSC.prettyprint(pos.get_element())

    pos = OSC.RelativeObjectPosition('Target',1,2,0,orientation=OSC.Orientation(h=0.2))
    OSC.prettyprint(pos.get_element())


def test_roadposition():
    pos = OSC.RoadPosition(1,2,reference_id='1')
    OSC.prettyprint(pos.get_element())

    pos = OSC.RelativeRoadPosition(1,2,entity='Ego')
    OSC.prettyprint(pos.get_element())

def test_laneposition():
    pos = OSC.LanePosition(1,2,lane_id='lane1',road_id='road1')
    OSC.prettyprint(pos.get_element())

    pos = OSC.RelativeLanePosition(1,2,lane_id=1,entity='Ego')
    OSC.prettyprint(pos.get_element())

def test_route_position():
    route = OSC.Route('myroute')

    route.add_waypoint(OSC.WorldPosition(),'shortest')

    route.add_waypoint(OSC.WorldPosition(1,1,1),'shortest')

    routepos = OSC.RoutePositionOfCurrentEntity(route,'Ego')
    OSC.prettyprint(routepos.get_element())
    routepos = OSC.RoutePositionInRoadCoordinates(route,1,3)
    OSC.prettyprint(routepos.get_element())
    routepos = OSC.RoutePositionInLaneCoordinates(route,1,'a',2)
    OSC.prettyprint(routepos.get_element())
