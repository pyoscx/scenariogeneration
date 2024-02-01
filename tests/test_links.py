"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import pytest
from scenariogeneration import xodr as pyodrx
from scenariogeneration import prettyprint
import numpy as np
from .xml_validator import version_validation, ValidationResponse


def test_link():
    link = pyodrx.links._Link("successor", "1")

    prettyprint(link.get_element())

    link = pyodrx.links._Link(
        "successor",
        "1",
        element_type=pyodrx.ElementType.road,
        contact_point=pyodrx.ContactPoint.start,
    )

    prettyprint(link.get_element())
    link2 = pyodrx.links._Link(
        "successor",
        "1",
        element_type=pyodrx.ElementType.road,
        contact_point=pyodrx.ContactPoint.start,
    )
    link3 = pyodrx.links._Link(
        "successor",
        "2",
        element_type=pyodrx.ElementType.road,
        contact_point=pyodrx.ContactPoint.start,
    )
    assert link == link2
    assert link != link3


def test_links():
    links = pyodrx.links._Links()
    prettyprint(links.get_element())
    link = pyodrx.links._Link("successor", "1")
    links.add_link(link)
    prettyprint(links.get_element())

    links2 = pyodrx.links._Links()
    links3 = pyodrx.links._Links()
    links2.add_link(pyodrx.links._Link("successor", "1"))
    links3.add_link(pyodrx.links._Link("successor", "1"))
    links3.add_link(pyodrx.links._Link("predecessor", "2"))
    assert links == links2
    assert links != links3
    with pytest.raises(TypeError):
        links.add_link("dummy")


def test_lanelinker():
    lane = pyodrx.Lane(a=3)
    lane._set_lane_id(1)
    lane.add_link("successor", "2")

    prettyprint(lane.get_element())

    assert (
        version_validation(
            "t_road_lanes_laneSection_left_lane", lane, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


def test_connection():
    con = pyodrx.Connection(1, 2, pyodrx.ContactPoint.start, 5)

    con.add_lanelink(1, -1)
    con.add_lanelink(2, -2)
    prettyprint(con.get_element(pyodrx.JunctionType.direct))

    con2 = pyodrx.Connection(1, 2, pyodrx.ContactPoint.start, 5)

    con2.add_lanelink(1, -1)
    con2.add_lanelink(2, -2)

    con3 = pyodrx.Connection(1, 2, pyodrx.ContactPoint.start, 5)

    con3.add_lanelink(1, -1)
    con3.add_lanelink(1, -2)

    assert con == con2
    assert con != con3
    assert (
        version_validation("t_junction_connection", con, wanted_schema="xodr")
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        pyodrx.Connection(1, 2, "dummy")


def test_junction():
    con1 = pyodrx.Connection(1, 2, pyodrx.ContactPoint.start)

    con1.add_lanelink(1, -1)
    con1.add_lanelink(2, -2)

    con2 = pyodrx.Connection(2, 1, pyodrx.ContactPoint.start)

    con2.add_lanelink(1, -1)
    con2.add_lanelink(2, -2)
    con2.add_lanelink(3, -3)

    junction = pyodrx.Junction("", 1)

    junction.add_connection(con1)
    junction.add_connection(con2)

    prettyprint(junction.get_element())

    junction2 = pyodrx.Junction("", 1)

    junction2.add_connection(con1)
    junction2.add_connection(con2)

    junction3 = pyodrx.Junction("a", 1)

    junction3.add_connection(con1)
    junction3.add_connection(con2)
    assert junction == junction2
    assert junction != junction3
    assert (
        version_validation("t_junction", junction, wanted_schema="xodr")
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        pyodrx.Junction("asdf", 1, "dummy")
    with pytest.raises(TypeError):
        junction.add_connection("dummy")


# road - road - road // -> - -> - ->
def test_create_lane_links_normalroad1():
    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing
    )

    geom = [pyodrx.Line(50)]
    geom.append(pyodrx.Arc(0.01, angle=np.pi / 2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])
    # create centerlanes
    for _ in geom:
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    # add roadmarks
    for i in range(len(geom)):
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
    for i in range(len(geom)):
        lanesec.append(pyodrx.LaneSection(0, lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    # create lanes
    for i in range(len(geom)):
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    # create roads
    road1 = pyodrx.Road(1, planview[0], lanes[0])
    road1.add_successor(pyodrx.ElementType.road, 2, pyodrx.ContactPoint.start)

    road2 = pyodrx.Road(2, planview[1], lanes[1])
    road2.add_predecessor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road, 3, pyodrx.ContactPoint.start)

    road3 = pyodrx.Road(3, planview[2], lanes[2])
    road3.add_predecessor(pyodrx.ElementType.road, 2, pyodrx.ContactPoint.end)

    # create the opendrive and add roads
    odr = pyodrx.OpenDrive("myroad")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert int(road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id()) == -1
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert int(road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id()) == 1

    assert (
        int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()) == -1
    )
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id()) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id()) == 1

    assert (
        int(road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()) == -1
    )
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert int(road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()) == 1
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


# road - junction - road // -> - -> - ->
def test_create_lane_links_junction1():
    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing
    )

    geom = [pyodrx.Line(50)]
    geom.append(pyodrx.Arc(0.01, angle=np.pi / 2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])
    # create centerlanes
    for _ in geom:
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
    # add roadmarks
    for i in range(len(geom)):
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
    # create lanesections
    for i in range(len(geom)):
        lanesec.append(pyodrx.LaneSection(0, lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
    # create lanes
    for i in range(len(geom)):
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    # create roads
    road1 = pyodrx.Road(1, planview[0], lanes[0])
    road1.add_successor(pyodrx.ElementType.junction, 1)

    road2 = pyodrx.Road(2, planview[1], lanes[1], road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road, 3, pyodrx.ContactPoint.start)

    road3 = pyodrx.Road(3, planview[2], lanes[2])
    road3.add_predecessor(pyodrx.ElementType.junction, 1)

    # create the opendrive and add roads
    odr = pyodrx.OpenDrive("myroad")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert (
        int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()) == -1
    )
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id()) == -1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id()) == 1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


# road - junction - road // <- - -> - <-
def test_create_lane_links_junction2():
    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing
    )

    geom = [pyodrx.Line(50)]
    geom.append(pyodrx.Arc(0.01, angle=np.pi / 2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])
        # create centerlanes
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
        # add roadmarks
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
        # create lanesections
        lanesec.append(pyodrx.LaneSection(0, lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
        # create lanes
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    # create roads
    road1 = pyodrx.Road(1, planview[0], lanes[0])
    road1.add_predecessor(pyodrx.ElementType.junction, 1)

    road2 = pyodrx.Road(2, planview[1], lanes[1], road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.start)
    road2.add_successor(pyodrx.ElementType.road, 3, pyodrx.ContactPoint.end)

    road3 = pyodrx.Road(3, planview[2], lanes[2])
    road3.add_successor(pyodrx.ElementType.junction, 1)

    # create the opendrive and add roads
    odr = pyodrx.OpenDrive("myroad")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert (
        int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()) == 1
    )
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id()) == 1
    assert (
        int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()) == -1
    )
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id()) == -1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


# road - junction - road // <- - -> - ->
def test_create_lane_links_junction3():
    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing
    )

    geom = [pyodrx.Line(50)]
    geom.append(pyodrx.Arc(0.01, angle=np.pi / 2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])
        # create centerlanes
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
        # add roadmarks
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
        # create lanesections
        lanesec.append(pyodrx.LaneSection(0, lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
        # create lanes
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    # create roads
    road1 = pyodrx.Road(1, planview[0], lanes[0])
    road1.add_predecessor(pyodrx.ElementType.junction, 1)

    road2 = pyodrx.Road(2, planview[1], lanes[1], road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.start)
    road2.add_successor(pyodrx.ElementType.road, 3, pyodrx.ContactPoint.start)

    road3 = pyodrx.Road(3, planview[2], lanes[2])
    road3.add_predecessor(pyodrx.ElementType.junction, 1)

    # create the opendrive and add roads
    odr = pyodrx.OpenDrive("myroad")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert (
        int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()) == 1
    )
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id()) == -1
    assert (
        int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()) == -1
    )
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id()) == 1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


# road - junction - road // -> - -> - <-
def test_create_lane_links_junction4():
    planview = []
    lanec = []
    lanel = []
    laner = []
    lanesec = []
    lanes = []

    rm = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid, 0.2, rule=pyodrx.MarkRule.no_passing
    )

    geom = [pyodrx.Line(50)]
    geom.append(pyodrx.Arc(0.01, angle=np.pi / 2))
    geom.append(pyodrx.Line(50))

    # create planviews
    for i in range(len(geom)):
        planview.append(pyodrx.PlanView())
        planview[i].add_geometry(geom[i])
        # create centerlanes
        lanec.append(pyodrx.Lane(a=3))
        lanel.append(pyodrx.Lane(a=3))
        laner.append(pyodrx.Lane(a=3))
        # add roadmarks
        lanec[i].add_roadmark(rm)
        lanel[i].add_roadmark(rm)
        laner[i].add_roadmark(rm)
        # create lanesections
        lanesec.append(pyodrx.LaneSection(0, lanec[i]))
        lanesec[i].add_right_lane(lanel[i])
        lanesec[i].add_left_lane(laner[i])
        # create lanes
        lanes.append(pyodrx.Lanes())
        lanes[i].add_lanesection(lanesec[i])

    # create roads
    road1 = pyodrx.Road(1, planview[0], lanes[0])
    road1.add_successor(pyodrx.ElementType.junction, 1)

    road2 = pyodrx.Road(2, planview[1], lanes[1], road_type=1)
    road2.add_predecessor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road, 3, pyodrx.ContactPoint.end)

    road3 = pyodrx.Road(3, planview[2], lanes[2])
    road3.add_successor(pyodrx.ElementType.junction, 1)

    # create the opendrive and add roads
    odr = pyodrx.OpenDrive("myroad")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.add_road(road3)

    odr.adjust_roads_and_lanes()

    assert (
        int(road2.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id()) == -1
    )
    assert int(road2.lanes.lanesections[0].rightlanes[0].links.get_successor_id()) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id()) == 1
    assert int(road2.lanes.lanesections[0].leftlanes[0].links.get_successor_id()) == -1

    assert road1.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road1.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None

    assert road3.lanes.lanesections[0].rightlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].rightlanes[0].links.get_successor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_predecessor_id() is None
    assert road3.lanes.lanesections[0].leftlanes[0].links.get_successor_id() is None
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


def test_junction_group():
    jg = pyodrx.JunctionGroup("my roundabout", 0)
    jg.add_junction(1)
    jg.add_junction(2)
    jg.add_junction(3)
    prettyprint(jg.get_element())
    jg2 = pyodrx.JunctionGroup("my roundabout", 0)
    jg2.add_junction(1)
    jg2.add_junction(2)
    jg2.add_junction(3)

    jg3 = pyodrx.JunctionGroup("my roundabout", 0)
    jg3.add_junction(1)
    jg3.add_junction(2)

    assert jg == jg2
    assert jg != jg3
    assert (
        version_validation("t_junctionGroup", jg, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_lanelinking_roads_pre_suc():
    road1 = pyodrx.create_road(pyodrx.Line(10), 0, 1, 1)
    road2 = pyodrx.create_road(pyodrx.Line(10), 1, 1, 1)
    road1.add_successor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.start)
    road2.add_predecessor(pyodrx.ElementType.road, 0, pyodrx.ContactPoint.end)
    odr = pyodrx.OpenDrive("test")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.adjust_roads_and_lanes()
    assert (
        road1.lanes.lanesections[0].leftlanes[0].links.links[0].link_type == "successor"
    )
    assert (
        road1.lanes.lanesections[0].rightlanes[0].links.links[0].link_type
        == "successor"
    )
    assert road1.lanes.lanesections[0].leftlanes[0].links.links[0].element_id == "1"
    assert road1.lanes.lanesections[0].rightlanes[0].links.links[0].element_id == "-1"

    assert (
        road2.lanes.lanesections[0].leftlanes[0].links.links[0].link_type
        == "predecessor"
    )
    assert (
        road2.lanes.lanesections[0].rightlanes[0].links.links[0].link_type
        == "predecessor"
    )
    assert road2.lanes.lanesections[0].leftlanes[0].links.links[0].element_id == "1"
    assert road2.lanes.lanesections[0].rightlanes[0].links.links[0].element_id == "-1"
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


def test_lanelinking_roads_suc_suc():
    road1 = pyodrx.create_road(pyodrx.Line(10), 0, 1, 1)
    road2 = pyodrx.create_road(pyodrx.Line(10), 1, 1, 1)
    road1.add_successor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.end)
    road2.add_successor(pyodrx.ElementType.road, 0, pyodrx.ContactPoint.end)
    odr = pyodrx.OpenDrive("test")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.adjust_roads_and_lanes()
    assert (
        road1.lanes.lanesections[0].leftlanes[0].links.links[0].link_type == "successor"
    )
    assert (
        road1.lanes.lanesections[0].rightlanes[0].links.links[0].link_type
        == "successor"
    )
    assert road1.lanes.lanesections[0].leftlanes[0].links.links[0].element_id == "-1"
    assert road1.lanes.lanesections[0].rightlanes[0].links.links[0].element_id == "1"

    assert (
        road2.lanes.lanesections[0].leftlanes[0].links.links[0].link_type == "successor"
    )
    assert (
        road2.lanes.lanesections[0].rightlanes[0].links.links[0].link_type
        == "successor"
    )
    assert road2.lanes.lanesections[0].leftlanes[0].links.links[0].element_id == "-1"
    assert road2.lanes.lanesections[0].rightlanes[0].links.links[0].element_id == "1"
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK


def test_lanelinking_roads_suc_suc():
    road1 = pyodrx.create_road(pyodrx.Line(10), 0, 1, 1)
    road2 = pyodrx.create_road(pyodrx.Line(10), 1, 1, 1)
    road1.add_predecessor(pyodrx.ElementType.road, 1, pyodrx.ContactPoint.start)
    road2.add_predecessor(pyodrx.ElementType.road, 0, pyodrx.ContactPoint.start)
    odr = pyodrx.OpenDrive("test")
    odr.add_road(road1)
    odr.add_road(road2)
    odr.adjust_roads_and_lanes()
    assert (
        road1.lanes.lanesections[0].leftlanes[0].links.links[0].link_type
        == "predecessor"
    )
    assert (
        road1.lanes.lanesections[0].rightlanes[0].links.links[0].link_type
        == "predecessor"
    )
    assert road1.lanes.lanesections[0].leftlanes[0].links.links[0].element_id == "-1"
    assert road1.lanes.lanesections[0].rightlanes[0].links.links[0].element_id == "1"

    assert (
        road2.lanes.lanesections[0].leftlanes[0].links.links[0].link_type
        == "predecessor"
    )
    assert (
        road2.lanes.lanesections[0].rightlanes[0].links.links[0].link_type
        == "predecessor"
    )
    assert road2.lanes.lanesections[0].leftlanes[0].links.links[0].element_id == "-1"
    assert road2.lanes.lanesections[0].rightlanes[0].links.links[0].element_id == "1"
    assert version_validation(None, odr, wanted_schema="xodr") == ValidationResponse.OK
