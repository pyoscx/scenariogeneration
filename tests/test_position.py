"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration
 
  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.
 
  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest

from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.xosc.position import WorldPosition


def test_worldposition_noinput():
    pos = OSC.WorldPosition()
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)
    pos2 = OSC.WorldPosition()
    pos3 = OSC.WorldPosition(1)
    assert pos == pos2
    assert pos != pos3
    pos4 = OSC.WorldPosition.parse(pos.get_element())
    assert pos == pos4


def test_worldposition_input():
    pos = OSC.WorldPosition(x=1, y=2, z=1.123)
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)
    pos2 = OSC.WorldPosition.parse(pos.get_element())
    assert pos == pos2


def test_relativeworldposition():

    pos = OSC.RelativeWorldPosition("Ego", 1, 2, 0)
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeWorldPosition("Ego", 1, 2, 0)
    pos3 = OSC.RelativeWorldPosition(
        "Target", 1, 2, 0, orientation=OSC.Orientation(h=0.2)
    )
    prettyprint(pos3.get_element())

    assert pos == pos2
    assert pos != pos3
    pos4 = OSC.RelativeWorldPosition.parse(pos.get_element())
    assert pos4 == pos
    pos5 = OSC.RelativeWorldPosition.parse(pos3.get_element())
    prettyprint(pos5.get_element())
    assert pos5 == pos3


def test_relativeobjectposition():

    pos = OSC.RelativeObjectPosition("Ego", 1, 2, 0)
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeObjectPosition("Ego", 1, 2, 0)
    pos3 = OSC.RelativeObjectPosition(
        "Target", 1, 2, 0, orientation=OSC.Orientation(h=0.2)
    )
    prettyprint(pos.get_element())

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RelativeObjectPosition.parse(pos3.get_element())
    assert pos3 == pos4


def test_roadposition():
    pos = OSC.RoadPosition(1, 2, reference_id="1")
    prettyprint(pos.get_element())
    pos2 = OSC.RoadPosition(1, 2, reference_id="1")
    pos3 = OSC.RoadPosition(1, 2, reference_id="3")

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RoadPosition.parse(pos.get_element())
    assert pos == pos4


def test_relativeroadposition():
    pos = OSC.RelativeRoadPosition(1, 2, "ego")
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeRoadPosition(1, 2, "ego")
    pos3 = OSC.RelativeRoadPosition(1, 2, "ego2")

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RelativeRoadPosition.parse(pos.get_element())
    assert pos == pos4


def test_laneposition():
    pos = OSC.LanePosition(1, 2, lane_id=1, road_id=2)
    prettyprint(pos.get_element())
    pos2 = OSC.LanePosition(1, 2, lane_id=1, road_id=2)
    pos3 = OSC.LanePosition(1, 1, lane_id=-1, road_id=2)
    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.LanePosition.parse(pos.get_element())
    assert pos == pos4


def test_relativelaneposition():

    pos = OSC.RelativeLanePosition(ds=1, lane_id=1, entity="Ego")
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeLanePosition(ds=1, lane_id=1, entity="Ego")
    pos3 = OSC.RelativeLanePosition(ds=1, lane_id=2, entity="Ego")

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RelativeLanePosition.parse(pos.get_element())
    assert pos == pos4


def test_route_position():
    route = OSC.Route("myroute")

    route.add_waypoint(OSC.WorldPosition(), OSC.RouteStrategy.shortest)

    route.add_waypoint(OSC.WorldPosition(1, 1, 1), OSC.RouteStrategy.shortest)

    routepos = OSC.RoutePositionOfCurrentEntity(route, "Ego")
    prettyprint(routepos.get_element())
    routepos2 = OSC.RoutePositionOfCurrentEntity(route, "Ego")
    routepos3 = OSC.RoutePositionOfCurrentEntity(route, "Ego1")
    assert routepos == routepos2
    assert routepos != routepos3

    routepos4 = OSC.RoutePositionOfCurrentEntity.parse(routepos.get_element())
    assert routepos == routepos4

    routepos = OSC.RoutePositionInRoadCoordinates(route, 1, 3)
    prettyprint(routepos.get_element())
    routepos2 = OSC.RoutePositionInRoadCoordinates(route, 1, 3)
    routepos3 = OSC.RoutePositionInRoadCoordinates(route, 2, 3)
    assert routepos == routepos2
    assert routepos != routepos3

    routepos4 = OSC.RoutePositionInRoadCoordinates.parse(routepos.get_element())
    assert routepos == routepos4

    routepos = OSC.RoutePositionInLaneCoordinates(route, 1, -1, 2)
    routepos2 = OSC.RoutePositionInLaneCoordinates(route, 1, -1, 2)
    routepos3 = OSC.RoutePositionInLaneCoordinates(route, 1, 1, 2)
    prettyprint(routepos.get_element())
    assert routepos == routepos2
    assert routepos != routepos3

    routepos4 = OSC.RoutePositionInLaneCoordinates.parse(routepos.get_element())
    assert routepos == routepos4


def test_trajectory_position():
    traj = OSC.Trajectory("my traj", False)
    traj.add_shape(OSC.Clothoid(0.001, 0.001, 100, OSC.WorldPosition()))
    pos = OSC.TrajectoryPosition(traj, 0)

    prettyprint(pos)
    pos2 = OSC.TrajectoryPosition(traj, 0)
    pos3 = OSC.TrajectoryPosition(traj, 0, 3)
    assert pos2 == pos
    assert pos3 != pos

    pos4 = OSC.TrajectoryPosition.parse(pos.get_element())
    assert pos == pos4


def test_geo_position():
    pos = OSC.GeoPosition(1, 1)
    pos2 = OSC.GeoPosition(1, 1)
    pos3 = OSC.GeoPosition(1, 1, 1)
    prettyprint(pos)
    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.GeoPosition.parse(pos.get_element())
    assert pos == pos4


# some fixtures for the factory test
traj = OSC.Trajectory("my_traj", False)
traj.add_shape(OSC.Clothoid(0.001, 0.001, 100, OSC.WorldPosition()))

route = OSC.Route("myroute")
route.add_waypoint(OSC.WorldPosition(), OSC.RouteStrategy.shortest)
route.add_waypoint(OSC.WorldPosition(1, 1, 1), OSC.RouteStrategy.shortest)


@pytest.mark.parametrize(
    "position",
    [
        OSC.WorldPosition(),
        OSC.RelativeWorldPosition("target", 0, 1, 0),
        OSC.RelativeObjectPosition("target", 1, 1),
        OSC.RoadPosition(
            10,
            20,
            0,
            orientation=OSC.Orientation(1, 1, 1, OSC.ReferenceContext.absolute),
        ),
        OSC.RelativeRoadPosition(
            10,
            0,
            "ego",
            orientation=OSC.Orientation(1, 1, 1, OSC.ReferenceContext.relative),
        ),
        OSC.LanePosition(
            10,
            1,
            -1,
            1,
            orientation=OSC.Orientation(1, 1, 1, OSC.ReferenceContext.relative),
        ),
        OSC.RelativeLanePosition(
            -1,
            "target",
            0,
            None,
            0.1,
            orientation=OSC.Orientation(1, 1, 1, OSC.ReferenceContext.relative),
        ),
        OSC.GeoPosition(10.11, 12.001),
        OSC.TrajectoryPosition(traj, 10),
        OSC.RoutePositionOfCurrentEntity(route, "Ego"),
        OSC.RoutePositionInRoadCoordinates(route, 1, 3),
        OSC.RoutePositionInLaneCoordinates(route, 1, 1, 2),
    ],
)
def test_position_factory(position):

    factoryoutput = OSC.position._PositionFactory.parse_position(position.get_element())
    prettyprint(position)
    prettyprint(factoryoutput)
    assert position == factoryoutput


def test_nurbs():
    cp1 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.1)
    cp2 = OSC.ControlPoint(OSC.WorldPosition(), 2, 0.2)
    cp3 = OSC.ControlPoint(OSC.WorldPosition(), 3, 0.3)

    nurb = OSC.Nurbs(2)
    nurb.add_control_point(cp1)
    nurb.add_control_point(cp2)
    nurb.add_control_point(cp3)
    nurb.add_knots([5, 4, 3, 2, 1])

    prettyprint(nurb.get_element())

    nurb2 = OSC.Nurbs(2)
    nurb2.add_control_point(cp1)
    nurb2.add_control_point(cp2)
    nurb2.add_control_point(cp3)
    nurb2.add_knots([5, 4, 3, 2, 1])

    nurb3 = OSC.Nurbs(2)
    nurb3.add_control_point(cp1)
    nurb3.add_control_point(cp2)
    nurb3.add_control_point(cp3)
    nurb3.add_knots([5, 4, 3, 2, 0.5])

    assert nurb == nurb2
    assert nurb != nurb3

    nurb4 = OSC.Nurbs.parse(nurb.get_element())
    assert nurb == nurb4
    nurb5_factory = OSC.position._ShapeFactory.parse_shape(nurb.get_element())
    assert nurb5_factory == nurb


def test_waypoint():
    wp = OSC.Waypoint(OSC.WorldPosition(), OSC.RouteStrategy.shortest)
    prettyprint(wp.get_element())
    wp2 = OSC.Waypoint(OSC.WorldPosition(), OSC.RouteStrategy.shortest)
    wp3 = OSC.Waypoint(OSC.WorldPosition(1), OSC.RouteStrategy.shortest)
    assert wp == wp2
    assert wp != wp3

    wp4 = OSC.Waypoint.parse(wp.get_element())
    assert wp == wp4


def test_route():
    route = OSC.Route("myroute")
    route.add_waypoint(OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
    route.add_waypoint(OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest)

    prettyprint(route.get_element())

    route2 = OSC.Route("myroute")
    route2.add_waypoint(OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
    route2.add_waypoint(OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest)

    route3 = OSC.Route("myroute")
    route3.add_waypoint(OSC.WorldPosition(0, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest)
    route3.add_waypoint(OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest)

    assert route == route2
    assert route != route3


def test_polyline():
    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(ds=10, lane_id=-3, entity="Ego"))
    positionlist.append(OSC.RelativeLanePosition(dsLane=10, lane_id=-3, entity="Ego"))
    positionlist.append(OSC.RelativeLanePosition(ds=10, lane_id=-3, entity="Ego"))
    positionlist.append(OSC.RelativeLanePosition(ds=10, lane_id=-3, entity="Ego"))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0, 0.5, 1, 1.5], positionlist)
    prettyprint(polyline.get_element())
    polyline2 = OSC.Polyline([0, 0.5, 1, 1.5], positionlist)
    polyline3 = OSC.Polyline([0, 0.5, 1, 1.3], positionlist)
    assert polyline == polyline2
    assert polyline != polyline3

    polyline4 = OSC.Polyline([], positionlist)
    # prettyprint(polyline4)
    polyline5 = OSC.Polyline.parse(polyline.get_element())
    prettyprint(polyline5)
    assert polyline == polyline5
    polyline_factory = OSC.position._ShapeFactory.parse_shape(polyline.get_element())
    assert polyline == polyline_factory


def test_clothoid():
    clot = OSC.Clothoid(1, 0.1, 10, OSC.WorldPosition(), 0, 1)
    prettyprint(clot.get_element())
    clot2 = OSC.Clothoid(1, 0.1, 10, OSC.WorldPosition(), 0, 1)
    clot3 = OSC.Clothoid(1, 0.1, 10, OSC.WorldPosition())
    prettyprint(clot3.get_element())
    assert clot == clot2
    assert clot != clot3
    clot4 = OSC.Clothoid.parse(clot.get_element())
    assert clot4 == clot
    clot5 = OSC.Clothoid.parse(clot3.get_element())
    assert clot3 == clot5
    clot_factory = OSC.position._ShapeFactory.parse_shape(clot.get_element())
    assert clot == clot_factory


def test_trajectory():
    positionlist = []
    # positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    # positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))

    positionlist.append(OSC.WorldPosition())
    positionlist.append(OSC.WorldPosition(1))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0, 0.5], positionlist)
    traj = OSC.Trajectory("my_trajectory", False)
    traj.add_shape(polyline)
    prettyprint(traj.get_element())
    traj2 = OSC.Trajectory("my_trajectory", False)
    traj2.add_shape(polyline)
    traj3 = OSC.Trajectory("my_trajectory2", False)
    assert traj == traj2
    assert traj != traj3
    traj4 = OSC.Trajectory.parse(traj.get_element())
    prettyprint(traj4.get_element())
    assert traj == traj4


def test_controlpoint():
    cp1 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.1)
    prettyprint(cp1)
    cp2 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.1)
    cp3 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.2)
    assert cp1 == cp2
    assert cp1 != cp3
    cp4 = OSC.ControlPoint.parse(cp1.get_element())
    assert cp1 == cp4
