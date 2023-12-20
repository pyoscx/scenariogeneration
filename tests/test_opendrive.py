"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""
from scenariogeneration.xodr.opendrive import OpenDrive
import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint
from .xml_validator import version_validation, ValidationResponse
import numpy as np


def test_simple_road():
    line1 = xodr.Line(100)
    planview = xodr.PlanView()
    planview.add_geometry(line1)

    rm = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2, rule=xodr.MarkRule.no_passing)

    lane1 = xodr.Lane(a=2)
    lane1.add_roadmark(rm)
    lanesec = xodr.LaneSection(0, lane1)

    lanes = xodr.Lanes()
    lanes.add_lanesection(lanesec)

    road = xodr.Road(1, planview, lanes)
    road.planview.adjust_geometries()

    prettyprint(road.get_element())
    assert (
        version_validation("t_road", road, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_link_road():
    planview = xodr.PlanView()
    planview.add_geometry(xodr.Line(100))
    lane1 = xodr.Lane(a=2)
    lane1.add_roadmark(
        xodr.RoadMark(xodr.RoadMarkType.solid, 0.2, rule=xodr.MarkRule.no_passing)
    )
    lanes = xodr.Lanes()
    lanes.add_lanesection(xodr.LaneSection(0, lane1))

    road = xodr.Road(1, planview, lanes)
    road.add_predecessor(xodr.ElementType.road, "1", xodr.ContactPoint.start)
    prettyprint(road.get_element())

    planview2 = xodr.PlanView()
    planview2.add_geometry(xodr.Line(100))
    lane12 = xodr.Lane(a=2)
    lane12.add_roadmark(
        xodr.RoadMark(xodr.RoadMarkType.solid, 0.2, rule=xodr.MarkRule.no_passing)
    )
    lanes2 = xodr.Lanes()
    lanes2.add_lanesection(xodr.LaneSection(0, lane12))

    road2 = xodr.Road(1, planview2, lanes2)
    road2.add_predecessor(xodr.ElementType.road, "1", xodr.ContactPoint.start)

    planview3 = xodr.PlanView()
    planview3.add_geometry(xodr.Line(120))
    lane13 = xodr.Lane(a=2)
    lane13.add_roadmark(
        xodr.RoadMark(xodr.RoadMarkType.solid, 0.2, rule=xodr.MarkRule.no_passing)
    )
    lanes3 = xodr.Lanes()
    lanes3.add_lanesection(xodr.LaneSection(0, lane13))

    road3 = xodr.Road(2, planview3, lanes3)
    road3.add_predecessor(xodr.ElementType.road, "1", xodr.ContactPoint.start)

    odr = xodr.OpenDrive("")
    odr2 = xodr.OpenDrive("")
    odr3 = xodr.OpenDrive("")
    odr.add_road(road)
    odr2.add_road(road2)
    odr3.add_road(road3)
    odr.adjust_roads_and_lanes()
    odr2.adjust_roads_and_lanes()
    odr3.adjust_roads_and_lanes()

    assert odr == odr2
    assert odr != odr3
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


@pytest.mark.parametrize(
    "data",
    [
        ([10, 100, -1, 1, 3]),
        ([10, 50, -1, 1, 3]),
        ([10, 100, -1, 1, 3]),
        ([10, 100, -1, 2, 3]),
        ([10, 100, -1, 10, 3]),
        ([10, 100, -1, 10, 5]),
    ],
)
def test_create_straight_road(data):
    road = xodr.create_road(
        [xodr.Line(data[1])], data[0], data[3], data[3], data[2], lane_width=data[4]
    )
    odr = xodr.OpenDrive("myroad")
    odr.add_road(road)
    odr.adjust_roads_and_lanes()

    redict = road.get_attributes()

    assert int(redict["id"]) == data[0]
    assert int(redict["length"]) == data[1]
    assert int(redict["junction"]) == data[2]
    assert len(road.lanes.lanesections[0].leftlanes) == data[3]
    assert len(road.lanes.lanesections[0].rightlanes) == data[3]
    assert road.lanes.lanesections[0].leftlanes[0].widths[0].a == data[4]
    assert road.lanes.lanesections[0].leftlanes[0].widths[0].b == 0
    assert road.lanes.lanesections[0].leftlanes[0].widths[0].c == 0
    assert road.lanes.lanesections[0].leftlanes[0].widths[0].d == 0
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


def test_road_type():
    rt = xodr.opendrive._Type(xodr.RoadType.motorway, 0, "SE")
    prettyprint(rt.get_element())
    rt2 = xodr.opendrive._Type(xodr.RoadType.motorway, 0, "SE")
    rt3 = xodr.opendrive._Type(xodr.RoadType.motorway, 0, "DE")
    assert rt == rt2
    assert rt != rt3

    rt = xodr.opendrive._Type(xodr.RoadType.motorway, 0, "SE", speed="no limit")
    prettyprint(rt.get_element())
    rt2 = xodr.opendrive._Type(xodr.RoadType.motorway, 0, "SE", speed="no limit")
    rt3 = xodr.opendrive._Type(xodr.RoadType.motorway, 1, "SE", speed="no limit")
    assert rt == rt2
    assert rt != rt3
    assert (
        version_validation("t_road_type", rt, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_road_with_road_types():
    xodr.create_road(xodr.Line(100), 0)
    road = xodr.create_road(xodr.Line(100), 0)
    road.add_type(xodr.RoadType.motorway, 0)
    prettyprint(road.get_element())

    road2 = xodr.create_road(xodr.Line(100), 0)
    road2.add_type(xodr.RoadType.motorway, 0)
    road3 = xodr.create_road(xodr.Line(50), 0)
    road3.add_type(xodr.RoadType.motorway, 0)

    odr = xodr.OpenDrive("")
    odr2 = xodr.OpenDrive("")
    odr3 = xodr.OpenDrive("")
    odr.add_road(road)
    odr2.add_road(road2)
    odr3.add_road(road3)
    odr.adjust_roads_and_lanes()
    odr2.adjust_roads_and_lanes()
    odr3.adjust_roads_and_lanes()

    assert road == road2
    assert road.planview != road3.planview
    assert odr == odr2
    assert odr != odr3
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


def test_road_with_repeating_objects():
    r1 = xodr.create_road(xodr.Line(100), 1)
    r2 = xodr.create_road(xodr.Line(100), 1)
    r3 = xodr.create_road(xodr.Line(100), 1)
    guardrail = xodr.Object(
        0, 0, height=2.0, zOffset=0, Type=xodr.ObjectType.barrier, name="railing"
    )
    odr = xodr.OpenDrive("")
    odr2 = xodr.OpenDrive("")
    odr3 = xodr.OpenDrive("")
    odr.add_road(r1)
    odr2.add_road(r2)
    odr3.add_road(r3)
    odr.adjust_roads_and_lanes()
    odr2.adjust_roads_and_lanes()
    odr3.adjust_roads_and_lanes()
    r3.add_object_roadside(guardrail, 4, 0, 0, xodr.RoadSide.both, 1, 0.1, 4, 1, 4, 1)
    prettyprint(odr3.get_element())

    assert r1 == r2
    assert r1 != r3
    assert odr == odr2
    assert odr != odr3
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


def test_header():
    h1 = xodr.opendrive._Header("hej", "1", "4")
    h2 = xodr.opendrive._Header("hej", "1", "4")
    h3 = xodr.opendrive._Header("hej", "1", "5")
    assert h1 == h2
    assert h1 != h3
    assert (
        version_validation("t_header", h1, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_odr_road_patching_connection_types():
    road1 = xodr.create_road(xodr.Line(100), 1, 1, 1)
    road2 = xodr.create_road(xodr.Line(100), 2, 1, 1)
    road3 = xodr.create_road(xodr.Line(100), 3, 1, 1)
    road4 = xodr.create_road(xodr.Line(100), 4, 1, 1)

    road1.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    road2.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.end)
    road3.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    road2.add_successor(xodr.ElementType.road, 3, xodr.ContactPoint.end)
    road3.add_predecessor(xodr.ElementType.road, 4, xodr.ContactPoint.start)
    road4.add_predecessor(xodr.ElementType.road, 3, xodr.ContactPoint.start)

    odr = xodr.OpenDrive("my_road")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)
    odr.add_road(road4)
    odr.adjust_roads_and_lanes()
    assert road1.planview.get_start_point() == (0, 0, 0)
    assert road2.planview.get_start_point() == (100.0, 0, 0)
    assert road3.planview.get_start_point() == (300.0, 0, np.pi)
    assert road4.planview.get_start_point() == (300.0, 0, 0)


def test_odr_road_patching_connection_types_wrong_types_successor():
    road1 = xodr.create_road(xodr.Line(100), 1, 1, 1)
    road2 = xodr.create_road(xodr.Line(100), 2, 1, 1)

    road1.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.start)
    road2.add_predecessor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    odr = xodr.OpenDrive("my_road")
    odr.add_road(road1)
    odr.add_road(road2)

    with pytest.raises(xodr.exceptions.MixingDrivingDirection) as e:
        odr.adjust_roads_and_lanes()


def test_odr_road_patching_connection_types_wrong_types_predecessor():
    road1 = xodr.create_road(xodr.Line(100), 1, 1, 1)
    road2 = xodr.create_road(xodr.Line(100), 2, 1, 1)

    road1.add_successor(xodr.ElementType.road, 2, xodr.ContactPoint.end)
    road2.add_successor(xodr.ElementType.road, 1, xodr.ContactPoint.start)

    odr = xodr.OpenDrive("my_road")
    odr.add_road(road1)
    odr.add_road(road2)

    with pytest.raises(xodr.exceptions.MixingDrivingDirection) as e:
        odr.adjust_roads_and_lanes()
