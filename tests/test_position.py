
import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
def test_worldposition_noinput():
    pos = OSC.WorldPosition()
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)

def test_worldposition_input():
    pos = OSC.WorldPosition(x=1,y=2,z=1.123)
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)


def test_relativeworldposition():
    
    pos = OSC.RelativeWorldPosition('Ego',1,2,0)
    prettyprint(pos.get_element())

    pos = OSC.RelativeWorldPosition('Target',1,2,0,orientation=OSC.Orientation(h=0.2))
    prettyprint(pos.get_element())


def test_relativeobjectposition():
    
    pos = OSC.RelativeObjectPosition('Ego',1,2,0)
    prettyprint(pos.get_element())

    pos = OSC.RelativeObjectPosition('Target',1,2,0,orientation=OSC.Orientation(h=0.2))
    prettyprint(pos.get_element())


def test_roadposition():
    pos = OSC.RoadPosition(1,2,reference_id='1')
    prettyprint(pos.get_element())

    pos = OSC.RelativeRoadPosition(1,2,entity='Ego')
    prettyprint(pos.get_element())

def test_laneposition():
    pos = OSC.LanePosition(1,2,lane_id='lane1',road_id='road1')
    prettyprint(pos.get_element())

    pos = OSC.RelativeLanePosition(1,2,lane_id=1,entity='Ego')
    prettyprint(pos.get_element())

def test_route_position():
    route = OSC.Route('myroute')

    route.add_waypoint(OSC.WorldPosition(),OSC.RouteStrategy.shortest)

    route.add_waypoint(OSC.WorldPosition(1,1,1),OSC.RouteStrategy.shortest)

    routepos = OSC.RoutePositionOfCurrentEntity(route,'Ego')
    prettyprint(routepos.get_element())
    routepos = OSC.RoutePositionInRoadCoordinates(route,1,3)
    prettyprint(routepos.get_element())
    routepos = OSC.RoutePositionInLaneCoordinates(route,1,'a',2)
    prettyprint(routepos.get_element())
