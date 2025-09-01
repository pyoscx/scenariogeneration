"""
scenariogeneration
https://github.com/pyoscx/scenariogeneration

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.

Copyright (c) 2022 The scenariogeneration Authors.

"""

import os

import pytest

from scenariogeneration import prettyprint
from scenariogeneration import xosc as OSC
from scenariogeneration.xosc.enumerations import _MINOR_VERSION

from .xml_validator import ValidationResponse, version_validation


@pytest.fixture(autouse=True)
def reset_version():
    OSC.enumerations.VersionBase().setVersion(minor=_MINOR_VERSION)


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
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK


def test_worldposition_input():
    pos = OSC.WorldPosition(x=1, y=2, z=1.123)
    pos.get_attributes()
    p = pos.get_element()
    prettyprint(p)
    pos2 = OSC.WorldPosition.parse(pos.get_element())
    assert pos == pos2
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK


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
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.RelativeWorldPosition("ego", 1, 1, 1, "dummy")


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
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.RelativeObjectPosition("ego", 1, 1, 1, "dummy")


def test_roadposition():
    pos = OSC.RoadPosition(1, 2, reference_id="1")
    prettyprint(pos.get_element())
    pos2 = OSC.RoadPosition(1, 2, reference_id="1")
    pos3 = OSC.RoadPosition(1, 2, reference_id="3")

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RoadPosition.parse(pos.get_element())
    assert pos == pos4
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.RoadPosition(1, 1, "2", "dummy")


def test_relativeroadposition():
    pos = OSC.RelativeRoadPosition(1, 2, "ego")
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeRoadPosition(1, 2, "ego")
    pos3 = OSC.RelativeRoadPosition(1, 2, "ego2")

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RelativeRoadPosition.parse(pos.get_element())
    assert pos == pos4
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.RelativeRoadPosition(1, 1, "ego", "dummy")


def test_laneposition():
    pos = OSC.LanePosition(1, 2, lane_id=1, road_id=2)
    prettyprint(pos.get_element())
    pos2 = OSC.LanePosition(1, 2, lane_id=1, road_id=2)
    pos3 = OSC.LanePosition(1, 1, lane_id=-1, road_id=2)
    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.LanePosition.parse(pos.get_element())
    assert pos == pos4
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.LanePosition(1, 1, 1, 1, "dummy")


def test_relativelaneposition():
    pos = OSC.RelativeLanePosition(ds=1, lane_id=1, entity="Ego")
    prettyprint(pos.get_element())
    pos2 = OSC.RelativeLanePosition(ds=1, lane_id=1, entity="Ego")
    pos3 = OSC.RelativeLanePosition(ds=1, lane_id=2, entity="Ego")

    assert pos == pos2
    assert pos != pos3

    pos4 = OSC.RelativeLanePosition.parse(pos.get_element())
    assert pos == pos4
    assert version_validation("Position", pos, 0) == ValidationResponse.OK
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK

    pos5 = OSC.RelativeLanePosition(dsLane=1, lane_id=2, entity="Ego")
    assert (
        version_validation("Position", pos5, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("Position", pos5, 1) == ValidationResponse.OK
    assert version_validation("Position", pos5, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.RelativeLanePosition(1, "1", 1, 3, orientation="dummy")
    with pytest.raises(OSC.NotEnoughInputArguments):
        OSC.RelativeLanePosition(1, "ego", 0)
    with pytest.raises(OSC.ToManyOptionalArguments):
        OSC.RelativeLanePosition(1, "ego", 0, 0, 0)


def test_route_position_entity():
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

    assert version_validation("Position", routepos, 0) == ValidationResponse.OK
    assert version_validation("Position", routepos, 1) == ValidationResponse.OK
    assert version_validation("Position", routepos, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.RoutePositionOfCurrentEntity("dummy")
    with pytest.raises(TypeError):
        OSC.RoutePositionOfCurrentEntity(route, "eog", "dummy")


def test_route_position_road_coordinates():
    routepos = OSC.RoutePositionInRoadCoordinates(route, 1, 3)
    prettyprint(routepos.get_element())
    routepos2 = OSC.RoutePositionInRoadCoordinates(route, 1, 3)
    routepos3 = OSC.RoutePositionInRoadCoordinates(route, 2, 3)
    assert routepos == routepos2
    assert routepos != routepos3

    routepos4 = OSC.RoutePositionInRoadCoordinates.parse(
        routepos.get_element()
    )
    assert routepos == routepos4

    assert version_validation("Position", routepos, 0) == ValidationResponse.OK
    assert version_validation("Position", routepos, 1) == ValidationResponse.OK
    assert version_validation("Position", routepos, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.RoutePositionInRoadCoordinates("dummy", 1, 1)
    with pytest.raises(TypeError):
        OSC.RoutePositionInRoadCoordinates(route, 1, 1, "dummy")


def test_route_position_lane_coordinates():
    routepos = OSC.RoutePositionInLaneCoordinates(route, 1, -1, 2)
    routepos2 = OSC.RoutePositionInLaneCoordinates(route, 1, -1, 2)
    routepos3 = OSC.RoutePositionInLaneCoordinates(route, 1, 1, 2)
    prettyprint(routepos.get_element())
    assert routepos == routepos2
    assert routepos != routepos3

    routepos4 = OSC.RoutePositionInLaneCoordinates.parse(
        routepos.get_element()
    )
    assert routepos == routepos4

    assert version_validation("Position", routepos, 0) == ValidationResponse.OK
    assert version_validation("Position", routepos, 1) == ValidationResponse.OK
    assert version_validation("Position", routepos, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.RoutePositionInLaneCoordinates("dummy", 1, 1, 1)
    with pytest.raises(TypeError):
        OSC.RoutePositionInLaneCoordinates(route, 1, 1, 1, "dummy")


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
    assert (
        version_validation("Position", pos, 0)
        == ValidationResponse.OSC_VERSION
    )
    assert version_validation("Position", pos, 1) == ValidationResponse.OK
    assert version_validation("Position", pos, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.TrajectoryPosition("dummy", 0)
    with pytest.raises(TypeError):
        OSC.TrajectoryPosition(traj, 0, 0, "dummy")


class TestGeoPosition:
    @pytest.fixture(name="geo_pos")
    def geo_pos(self):
        return OSC.GeoPosition(
            52.1, 13.4, 100.0, OSC.Orientation(), vertical_road_selection=2
        )

    def test_init_and_attributes(self, geo_pos):
        assert geo_pos.latitude == 52.1
        assert geo_pos.longitude == 13.4
        assert geo_pos.height == 100.0
        assert isinstance(geo_pos.orientation, OSC.Orientation)
        assert geo_pos.vertical_road_selection == 2

    def test_attributes_v2(self, geo_pos):
        OSC.VersionBase().setVersion(minor=2)
        attrs = geo_pos.get_attributes()
        assert "verticalRoadSelection" not in attrs

    def test_equality(self, geo_pos):
        pos2 = OSC.GeoPosition(52.1, 13.4, 100.0, vertical_road_selection=2)
        assert geo_pos == pos2

    def test_equality_v2(self, geo_pos):
        OSC.VersionBase().setVersion(minor=2)
        pos3 = OSC.GeoPosition(52.1, 13.4, 100.0)
        assert geo_pos == pos3

    def test_neq(self, geo_pos):
        pos3 = OSC.GeoPosition(52.1, 13.4, 101.0)
        assert geo_pos != pos3

    def test_parse_and_get_element(self, geo_pos):
        element = geo_pos.get_element()
        parsed = OSC.GeoPosition.parse(element)
        assert geo_pos == parsed

    def test_missing_attributes(self):
        pos = OSC.GeoPosition(52.1, 13.4)
        assert pos.height is None
        assert pos.orientation == OSC.Orientation()
        assert pos.vertical_road_selection is None

    def test_valid_and_invalid_types(self):
        OSC.GeoPosition("52.1", 13.4)
        OSC.GeoPosition(52.1, "13.4")
        OSC.GeoPosition(52.1, 13.4, "100.0")

        with pytest.raises(TypeError):
            OSC.GeoPosition(52.1, 13.4, 100.0, orientation="dummy")
        with pytest.raises(TypeError):
            OSC.GeoPosition(52.1, 13.4, 100.0, orientation="invalid")
        with pytest.raises(ValueError):
            OSC.GeoPosition(
                52.1, 13.4, 100.0, vertical_road_selection="invalid"
            )

    @pytest.mark.parametrize("version", [1, 2, 3])
    def test_version_validation(self, version, geo_pos):
        assert (
            version_validation("Position", geo_pos, version)
            == ValidationResponse.OK
        )


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
            orientation=OSC.Orientation(
                1, 1, 1, OSC.ReferenceContext.absolute
            ),
        ),
        OSC.RelativeRoadPosition(
            10,
            0,
            "ego",
            orientation=OSC.Orientation(
                1, 1, 1, OSC.ReferenceContext.relative
            ),
        ),
        OSC.LanePosition(
            10,
            1,
            -1,
            1,
            orientation=OSC.Orientation(
                1, 1, 1, OSC.ReferenceContext.relative
            ),
        ),
        OSC.RelativeLanePosition(
            -1,
            "target",
            0,
            None,
            0.1,
            orientation=OSC.Orientation(
                1, 1, 1, OSC.ReferenceContext.relative
            ),
        ),
        OSC.GeoPosition(10.11, 12.001),
        OSC.TrajectoryPosition(traj, 10),
        OSC.RoutePositionOfCurrentEntity(route, "Ego"),
        OSC.RoutePositionInRoadCoordinates(route, 1, 3),
        OSC.RoutePositionInLaneCoordinates(route, 1, 1, 2),
    ],
)
def test_position_factory(position):
    factoryoutput = OSC.position._PositionFactory.parse_position(
        position.get_element()
    )
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

    assert version_validation("Shape", nurb, 0) == ValidationResponse.OK
    assert version_validation("Shape", nurb, 1) == ValidationResponse.OK
    assert version_validation("Shape", nurb, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        nurb.add_control_point("dummy")


def test_waypoint():
    wp = OSC.Waypoint(OSC.WorldPosition(), OSC.RouteStrategy.shortest)
    prettyprint(wp.get_element())
    wp2 = OSC.Waypoint(OSC.WorldPosition(), OSC.RouteStrategy.shortest)
    wp3 = OSC.Waypoint(OSC.WorldPosition(1), OSC.RouteStrategy.shortest)
    assert wp == wp2
    assert wp != wp3

    wp4 = OSC.Waypoint.parse(wp.get_element())
    assert wp == wp4
    assert version_validation("Waypoint", wp, 0) == ValidationResponse.OK
    assert version_validation("Waypoint", wp, 1) == ValidationResponse.OK
    assert version_validation("Waypoint", wp, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.Waypoint("dummy")
    with pytest.raises(ValueError):
        OSC.Waypoint(OSC.WorldPosition(), "dummy")


def test_route(tmpdir):
    route = OSC.Route("myroute")
    route.add_waypoint(
        OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    route.add_waypoint(
        OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )

    prettyprint(route.get_element())

    route2 = OSC.Route("myroute")
    route2.add_waypoint(
        OSC.WorldPosition(0, 0, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    route2.add_waypoint(
        OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )

    route3 = OSC.Route("myroute")
    route3.add_waypoint(
        OSC.WorldPosition(0, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    route3.add_waypoint(
        OSC.WorldPosition(1, 1, 0, 0, 0, 0), OSC.RouteStrategy.shortest
    )
    route.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "RouteCatalog",
        "test catalog",
        "Mandolin",
    )
    assert route == route2
    assert route != route3
    assert version_validation("Route", route, 0) == ValidationResponse.OK
    assert version_validation("Route", route, 1) == ValidationResponse.OK
    assert version_validation("Route", route, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        route.add_waypoint("dummy", OSC.RouteStrategy.shortest)
    with pytest.raises(ValueError):
        route.add_waypoint(OSC.WorldPosition(), "dummy")


def test_polyline():
    positionlist = []
    positionlist.append(
        OSC.RelativeLanePosition(ds=10, lane_id=-3, entity="Ego")
    )
    positionlist.append(
        OSC.RelativeLanePosition(ds=11, lane_id=-3, entity="Ego")
    )
    positionlist.append(
        OSC.RelativeLanePosition(ds=10, lane_id=-3, entity="Ego")
    )
    positionlist.append(
        OSC.RelativeLanePosition(ds=10, lane_id=-3, entity="Ego")
    )
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
    polyline_factory = OSC.position._ShapeFactory.parse_shape(
        polyline.get_element()
    )
    assert polyline == polyline_factory
    assert version_validation("Shape", polyline, 0) == ValidationResponse.OK
    assert version_validation("Shape", polyline, 1) == ValidationResponse.OK
    assert version_validation("Shape", polyline, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.Polyline([], [OSC.WorldPosition(), "dummy"])


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

    assert version_validation("Shape", clot, 0) == ValidationResponse.OK
    assert version_validation("Shape", clot, 1) == ValidationResponse.OK
    assert version_validation("Shape", clot, 2) == ValidationResponse.OK

    with pytest.raises(TypeError):
        OSC.Clothoid(0, 0, 0, "dummy")


def test_trajectory(tmpdir):
    positionlist = []
    # positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    # positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))

    positionlist.append(OSC.WorldPosition())
    positionlist.append(OSC.WorldPosition(1))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0, 0.5], positionlist)
    traj = OSC.Trajectory("my_trajectory", False)
    traj.add_shape(polyline)
    param = OSC.Parameter(
        "my_param", OSC.ParameterType.string, "test parameter"
    )
    traj.add_parameter(param)
    prettyprint(traj.get_element())
    traj2 = OSC.Trajectory("my_trajectory", False)
    traj2.add_shape(polyline)
    traj2.add_parameter(param)
    traj3 = OSC.Trajectory("my_trajectory2", False)
    assert traj == traj2
    assert traj != traj3
    traj4 = OSC.Trajectory.parse(traj.get_element())
    prettyprint(traj4.get_element())
    assert traj == traj4
    assert param == traj4.parameters.parameters[0]

    assert version_validation("Trajectory", traj, 0) == ValidationResponse.OK
    assert version_validation("Trajectory", traj, 1) == ValidationResponse.OK
    assert version_validation("Trajectory", traj, 2) == ValidationResponse.OK
    traj.dump_to_catalog(
        os.path.join(tmpdir, "my_catalog.xosc"),
        "TrajectoryCatalog",
        "test catalog",
        "Mandolin",
    )
    with pytest.raises(TypeError):
        traj.add_parameter("dummy")
    with pytest.raises(TypeError):
        traj.add_shape("dummy")
    with pytest.raises(OSC.NotEnoughInputArguments):
        traj = OSC.Trajectory("my_traj", False)
        traj.get_element()


def test_controlpoint():
    cp1 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.1)
    prettyprint(cp1)
    cp2 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.1)
    cp3 = OSC.ControlPoint(OSC.WorldPosition(), 1, 0.2)
    assert cp1 == cp2
    assert cp1 != cp3
    cp4 = OSC.ControlPoint.parse(cp1.get_element())
    assert cp1 == cp4

    assert version_validation("ControlPoint", cp1, 0) == ValidationResponse.OK
    assert version_validation("ControlPoint", cp1, 1) == ValidationResponse.OK
    assert version_validation("ControlPoint", cp1, 2) == ValidationResponse.OK
    with pytest.raises(TypeError):
        OSC.ControlPoint("dummy")


class TestPolygon:
    def setup_method(self):
        self.polygon = OSC.Polygon(
            [
                OSC.WorldPosition(0, 0, 0),
                OSC.WorldPosition(1, 0, 0),
                OSC.WorldPosition(1, 1, 0),
                OSC.WorldPosition(0, 1, 0),
            ]
        )
        self.polygon.setVersion(1, 3)

    def test_polygon_base(self):
        prettyprint(self.polygon)

    def test_polygon_to_few_points(self):
        with pytest.raises(ValueError):
            OSC.Polygon([OSC.WorldPosition(0, 0, 0)])

    def test_polugon_input_not_positions(self):
        with pytest.raises(TypeError):
            OSC.Polygon(
                [
                    OSC.WorldPosition(0, 0, 0),
                    OSC.WorldPosition(0, 0, 0),
                    "dummy",
                ]
            )

    def test_polygon_equality(self):
        polygon2 = OSC.Polygon(
            [
                OSC.WorldPosition(0, 0, 0),
                OSC.WorldPosition(1, 0, 0),
                OSC.WorldPosition(1, 1, 0),
                OSC.WorldPosition(0, 1, 0),
            ]
        )
        assert self.polygon == polygon2

        polygon3 = OSC.Polygon(
            [
                OSC.WorldPosition(0, 0, 0),
                OSC.WorldPosition(1, 1, 0),
                OSC.WorldPosition(1, 2, 0),
                OSC.WorldPosition(0, 2, 0),
            ]
        )
        assert self.polygon != polygon3

    def test_polygon_parse(self):
        polygon = self.polygon.get_element()
        parsed_polygon = OSC.Polygon.parse(polygon)
        assert self.polygon == parsed_polygon

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        assert version_validation("Polygon", self.polygon, version) == expected


class TestRoadRange:
    def setup_method(self):
        self.roadrange = OSC.RoadRange("10")
        self.roadrange.add_cursor("0")
        self.roadrange.add_cursor("1")
        self.roadrange.setVersion(1, 3)

        self.to_few_cursors = (
            "At least two road cursors are required for a RoadRange"
        )

    def test_roadrange_base(self):
        prettyprint(self.roadrange.get_element())

    def test_roadrange_equality(self):
        roadrange2 = OSC.RoadRange("10")
        roadrange2.add_cursor("0")
        roadrange2.add_cursor("1")
        assert self.roadrange == roadrange2

        roadrange3 = OSC.RoadRange("20")
        roadrange3.add_cursor("0")
        roadrange3.add_cursor("1")
        assert self.roadrange != roadrange3

    def test_add_cursor(self):
        self.roadrange.add_cursor("2")
        assert len(self.roadrange.roadcursors) == 3

    def test_parse(self):
        road_range = self.roadrange.get_element()
        parsed_roadrange = OSC.RoadRange.parse(road_range)
        assert self.roadrange == parsed_roadrange

    @pytest.mark.parametrize(
        ["version", "expected"],
        [
            (0, ValidationResponse.OSC_VERSION),
            (1, ValidationResponse.OSC_VERSION),
            (2, ValidationResponse.OSC_VERSION),
            (3, ValidationResponse.OK),
        ],
    )
    def test_validate_xml(self, version, expected):
        assert (
            version_validation("RoadRange", self.roadrange, version)
            == expected
        )

    def test_number_of_road_cursors(self):
        self.roadrange_basic = OSC.RoadRange()
        self.roadrange_basic.setVersion(1, 3)
        assert len(self.roadrange_basic.roadcursors) == 0
        with pytest.raises(ValueError) as to_few_cursors:
            self.roadrange_basic.get_element()
        assert str(to_few_cursors.value) == self.to_few_cursors

        self.roadrange_basic.add_cursor("0")
        assert len(self.roadrange_basic.roadcursors) == 1
        with pytest.raises(ValueError) as to_few_cursors:
            self.roadrange_basic.get_element()
        assert str(to_few_cursors.value) == self.to_few_cursors
        self.roadrange_basic.add_cursor("1")
        assert len(self.roadrange_basic.roadcursors) == 2
        self.roadrange_basic.get_element()

    def test_road_range_with_lanes(self):
        rr = OSC.RoadRange("10")
        rr.add_cursor("roadA", 0.0, [1, 2])
        rr.add_cursor("roadA", 100.0, [2])
        rr.setVersion(1, 3)
        element = rr.get_element()
        parsed = OSC.RoadRange.parse(element)
        assert rr == parsed
        assert parsed.roadcursors[0][2] == [1, 2]
        assert parsed.roadcursors[1][2] == [2]


class TestClothoidSpline:
    def setup_method(self):
        self.first_segment_position = [
            OSC.WorldPosition(0, 0, 0, 0, 0, 0),
        ]
        self.second_segment_position = [
            OSC.WorldPosition(1, 1, 0, 0, 0, 0),
        ]
        self.segments = [
            OSC.ClothoidSplineSegment(
                0.00, 0.01, 50.0, 0.0, 0.0, self.first_segment_position
            ),
            OSC.ClothoidSplineSegment(
                0.01, 0.02, 50.0, 0.0, 0.0, self.second_segment_position
            ),
        ]
        self.clothoid_spline = OSC.ClothoidSpline(
            segments=self.segments, time_end=5.0
        )
        self.clothoid_spline.setVersion(1, 3)

    def test_clothoid_spline_version_validation(self):
        assert (
            version_validation("Shape", self.clothoid_spline, 0)
            == ValidationResponse.OSC_VERSION
        )
        assert (
            version_validation("Shape", self.clothoid_spline, 1)
            == ValidationResponse.OSC_VERSION
        )
        assert (
            version_validation("Shape", self.clothoid_spline, 2)
            == ValidationResponse.OSC_VERSION
        )

    def test_clothoid_spline_equality(self):
        clothoid_spline2 = OSC.ClothoidSpline(
            segments=self.segments, time_end=5.0
        )
        assert self.clothoid_spline == clothoid_spline2

        clothoid_spline3 = OSC.ClothoidSpline(
            segments=self.segments, time_end=6.0
        )
        assert self.clothoid_spline != clothoid_spline3

    def test_clothoid_spline_parse(self):
        clothoid_spline_element = self.clothoid_spline.get_element()
        parsed_clothoid_spline = OSC.ClothoidSpline.parse(
            clothoid_spline_element
        )
        assert self.clothoid_spline == parsed_clothoid_spline

    def test_clothoid_spline_factory(self):
        clothoid_spline_element = self.clothoid_spline.get_element()
        factory_output = OSC.position._ShapeFactory.parse_shape(
            clothoid_spline_element
        )
        assert self.clothoid_spline == factory_output

    def test_clothoid_spline_prettyprint(self):
        prettyprint(self.clothoid_spline)
