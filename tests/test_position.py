

import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
def test_worldposition_noinput():
    pos = OSC.WorldPosition()
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)
    pos2 = OSC.WorldPosition()
    pos3 = OSC.WorldPosition(1)
    assert pos == pos2
    assert pos != pos3
    
def test_worldposition_input():
    pos = OSC.WorldPosition(x=1,y=2,z=1.123)
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)


def test_relativeworldposition():
    
    pos = OSC.RelativeWorldPosition('Ego',1,2,0)
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeWorldPosition('Ego',1,2,0)
    pos3 = OSC.RelativeWorldPosition('Target',1,2,0,orientation=OSC.Orientation(h=0.2))
    prettyprint(pos3.get_element())

    assert pos == pos2
    assert pos != pos3
    
def test_relativeobjectposition():
    
    pos = OSC.RelativeObjectPosition('Ego',1,2,0)
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeObjectPosition('Ego',1,2,0)
    pos3 = OSC.RelativeObjectPosition('Target',1,2,0,orientation=OSC.Orientation(h=0.2))
    prettyprint(pos.get_element())

    assert pos == pos2
    assert pos != pos3

def test_roadposition():
    pos = OSC.RoadPosition(1,2,reference_id='1')
    prettyprint(pos.get_element())
    pos2 = OSC.RoadPosition(1,2,reference_id='1')
    pos3 = OSC.RoadPosition(1,2,reference_id='3')


    assert pos == pos2
    assert pos != pos3

def test_relativeroadposition():
    pos = OSC.RelativeRoadPosition(1,2,'ego')
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeRoadPosition(1,2,'ego')
    pos3 = OSC.RelativeRoadPosition(1,2,'ego2')


    assert pos == pos2
    assert pos != pos3
def test_laneposition():
    pos = OSC.LanePosition(1,2,lane_id='lane1',road_id='road1')
    prettyprint(pos.get_element())
    pos2 = OSC.LanePosition(1,2,lane_id='lane1',road_id='road1')
    pos3 = OSC.LanePosition(1,1,lane_id='lane1',road_id='road1')
    assert pos == pos2
    assert pos != pos3

def test_relativelaneposition():

    pos = OSC.RelativeLanePosition(ds=1,lane_id=1,entity='Ego')
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeLanePosition(ds=1,lane_id=1,entity='Ego')
    pos3 = OSC.RelativeLanePosition(ds=1,lane_id=2,entity='Ego')

    assert pos == pos2
    assert pos != pos3

def test_route_position():
    route = OSC.Route('myroute')

    route.add_waypoint(OSC.WorldPosition(),OSC.RouteStrategy.shortest)

    route.add_waypoint(OSC.WorldPosition(1,1,1),OSC.RouteStrategy.shortest)

    routepos = OSC.RoutePositionOfCurrentEntity(route,'Ego')
    prettyprint(routepos.get_element())
    routepos2 = OSC.RoutePositionOfCurrentEntity(route,'Ego')
    routepos3 = OSC.RoutePositionOfCurrentEntity(route,'Ego1')
    assert routepos == routepos2
    assert routepos != routepos3

    routepos = OSC.RoutePositionInRoadCoordinates(route,1,3)
    prettyprint(routepos.get_element())
    routepos2 = OSC.RoutePositionInRoadCoordinates(route,1,3)
    routepos3 = OSC.RoutePositionInRoadCoordinates(route,2,3)
    assert routepos == routepos2
    assert routepos != routepos3

    routepos = OSC.RoutePositionInLaneCoordinates(route,1,'a',2)
    routepos2 = OSC.RoutePositionInLaneCoordinates(route,1,'a',2)
    routepos3 = OSC.RoutePositionInLaneCoordinates(route,1,'b',2)
    prettyprint(routepos.get_element())
    assert routepos == routepos2
    assert routepos != routepos3

def test_trajectory_position():
    traj = OSC.Trajectory('my traj',False)
    traj.add_shape(OSC.Clothoid(0.001,0.001,100,OSC.WorldPosition()))
    pos = OSC.TrajectoryPosition(traj,0)

    prettyprint(pos)
    pos2 = OSC.TrajectoryPosition(traj,0)
    pos3 = OSC.TrajectoryPosition(traj,0,3)
    assert pos2 == pos
    assert pos3 != pos

def test_geo_position():
    pos = OSC.GeoPosition(1,1)
    pos2 = OSC.GeoPosition(1,1)
    pos3 = OSC.GeoPosition(1,1,1)
    prettyprint(pos)
    assert pos == pos2
    assert pos != pos3