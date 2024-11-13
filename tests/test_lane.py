"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""

import pytest


from scenariogeneration import xodr
from scenariogeneration import prettyprint
from .xml_validator import version_validation, ValidationResponse


def test_roadline():
    line = xodr.RoadLine()

    prettyprint(line.get_element())
    line = xodr.RoadLine(
        1, 2, 3, 5, 1, xodr.MarkRule.no_passing, xodr.RoadMarkColor.standard
    )
    prettyprint(line.get_element())
    line2 = xodr.RoadLine(
        1, 2, 3, 5, 1, xodr.MarkRule.no_passing, xodr.RoadMarkColor.standard
    )
    line3 = xodr.RoadLine(
        1, 2, 3, 5, 1, xodr.MarkRule.none, xodr.RoadMarkColor.standard
    )
    assert line == line2
    assert line != line3
    with pytest.raises(TypeError):
        xodr.RoadLine(rule="dummy")

    with pytest.raises(TypeError):
        xodr.RoadLine(color="dummy")


def test_roadline_offset_calcs():
    line = xodr.RoadLine(1, 3, 3, 0, 0)
    line.adjust_remainder(10)
    assert line._remainder == 1
    line.adjust_remainder(10, 1)
    assert line._remainder == 0

    line._remainder = 0
    line.adjust_soffset(10)
    assert line.soffset == 1
    line.adjust_soffset(10, 1)
    assert line.soffset == 0
    assert (
        version_validation(
            "t_road_lanes_laneSection_lcr_lane_roadMark_type_line",
            line,
            wanted_schema="xodr",
        )
        == ValidationResponse.OK
    )


def test_explicit_roadline():
    line = xodr.ExplicitRoadLine()

    prettyprint(line.get_element())
    line = xodr.ExplicitRoadLine(1, 2, 5, 1, xodr.MarkRule.no_passing)
    prettyprint(line.get_element())
    line2 = xodr.ExplicitRoadLine(1, 2, 5, 1, xodr.MarkRule.no_passing)
    line3 = xodr.RoadLine(1, 2, 5, 1, xodr.MarkRule.none)
    assert line == line2
    assert line != line3
    assert (
        version_validation(
            "t_road_lanes_laneSection_lcr_lane_roadMark_explicit_line",
            line,
            wanted_schema="xodr",
        )
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        xodr.ExplicitRoadLine(rule="dummy")


def test_roadmark():
    mark = xodr.RoadMark(xodr.RoadMarkType.solid, 0.2)
    prettyprint(mark.get_element())
    mark = xodr.RoadMark(
        xodr.RoadMarkType.solid,
        0.2,
        1,
        1,
        1,
        0,
        xodr.MarkRule.no_passing,
        xodr.RoadMarkColor.standard,
    )
    mark.add_explicit_road_line(xodr.ExplicitRoadLine(1, 2, 3, 4))
    prettyprint(mark.get_element())
    mark2 = xodr.RoadMark(
        xodr.RoadMarkType.solid,
        0.2,
        1,
        1,
        1,
        0,
        xodr.MarkRule.no_passing,
        xodr.RoadMarkColor.standard,
    )
    mark2.add_explicit_road_line(xodr.ExplicitRoadLine(1, 2, 3, 4))
    mark3 = xodr.RoadMark(
        xodr.RoadMarkType.solid,
        0.2,
        1,
        1,
        2,
        0,
        xodr.MarkRule.no_passing,
        xodr.RoadMarkColor.standard,
    )
    mark3.add_explicit_road_line(xodr.ExplicitRoadLine(1, 2, 3, 4))
    assert mark == mark2
    assert mark != mark3

    mark4 = xodr.RoadMark(xodr.RoadMarkType.solid_solid)
    mark4.add_specific_road_line(xodr.RoadLine(0.2, 0, 0, 0.2, 0))
    mark4.add_specific_road_line(xodr.RoadLine(0.2, 0, 0, 0.2, 0))

    prettyprint(mark4.get_element())
    assert (
        version_validation(
            "t_road_lanes_laneSection_lcr_lane_roadMark", mark, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )

    with pytest.raises(TypeError):
        xodr.RoadMark("dummy")

    with pytest.raises(TypeError):
        xodr.RoadMark("solid", color="dummy")

    with pytest.raises(TypeError):
        xodr.RoadMark("solid", marking_weight="dummy")

    with pytest.raises(TypeError):
        xodr.RoadMark("solid", laneChange="dummy")


def test_poly3struct():
    ps1 = xodr.lane._poly3struct(1, 2, 3, 4, 5)
    ps2 = xodr.lane._poly3struct(1, 2, 3, 4, 5)
    ps3 = xodr.lane._poly3struct(2, 2, 3, 4, 5)
    assert ps1 == ps2
    assert ps1 != ps3


def test_lane():
    lane = xodr.Lane()
    lane._set_lane_id(1)
    lane.add_userdata(xodr.UserData("key", "value"))
    prettyprint(lane.get_element())
    lane = xodr.Lane(xodr.LaneType.driving, 1, 1, 1, 1, 2)
    lane._set_lane_id(1)
    prettyprint(lane.get_element())

    lane2 = xodr.Lane(xodr.LaneType.driving, 1, 1, 1, 1, 2)
    lane2._set_lane_id(1)
    lane3 = xodr.Lane(xodr.LaneType.driving, 1, 1, 1, 3, 2)
    lane3._set_lane_id(1)
    assert lane == lane2
    assert lane != lane3
    assert (
        version_validation(
            "t_road_lanes_laneSection_left_lane", lane, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )
    lane3._set_lane_id(-1)
    assert (
        version_validation(
            "t_road_lanes_laneSection_right_lane", lane3, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )
    lane3._set_lane_id(0)
    assert (
        version_validation(
            "t_road_lanes_laneSection_center_lane", lane3, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )

    with pytest.raises(TypeError):
        xodr.Lane("dummy")

    with pytest.raises(TypeError):
        lane.add_roadmark("dummy")


def test_lane_with_multiple_widths():
    lane = xodr.Lane()
    lane._set_lane_id(1)
    prettyprint(lane.get_element())
    lane = xodr.Lane(xodr.LaneType.driving, 1, 1, 1, 1, 2)
    lane.add_lane_width(1, 2, 3, 4, 5)

    lane._set_lane_id(1)
    prettyprint(lane.get_element())

    lane2 = xodr.Lane(xodr.LaneType.driving, 1, 1, 1, 1, 2)
    lane2._set_lane_id(1)
    lane2.add_lane_width(1, 2, 3, 4, 5)
    lane3 = xodr.Lane(xodr.LaneType.driving, 1, 1, 1, 3, 2)
    lane3._set_lane_id(1)
    lane3.add_lane_width(1, 2, 3, 4, 6)

    assert lane == lane2
    assert lane != lane3
    assert (
        version_validation(
            "t_road_lanes_laneSection_left_lane", lane, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


def test_lane_with_height():
    lane = xodr.Lane(xodr.LaneType.sidewalk, 1, 1, 1, 1, 2)
    lane._set_lane_id(1)
    lane.add_height(0.15)
    prettyprint(lane.get_element())
    assert (
        version_validation(
            "t_road_lanes_laneSection_left_lane", lane, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


def test_lane_with_material():
    lane = xodr.Lane(a=3)
    lane._set_lane_id(1)
    lane.add_lane_material(friction=1.1)
    lane.add_lane_material(friction=1.2, soffset=2.0)
    lane.add_lane_material(friction=1.3, soffset=1.0)
    prettyprint(lane.get_element())
    assert (
        version_validation(
            "t_road_lanes_laneSection_left_lane", lane, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


def test_lane_with_roadmarks():
    lane = xodr.Lane()
    lane._set_lane_id(1)
    lane.add_roadmark(xodr.std_roadmark_broken())
    lane2 = xodr.Lane()
    lane2._set_lane_id(1)
    lane2.add_roadmark(xodr.std_roadmark_broken())
    lane3 = xodr.Lane()
    lane3._set_lane_id(1)
    lane3.add_roadmark(xodr.std_roadmark_broken())
    lane3.add_roadmark(xodr.std_roadmark_solid())
    prettyprint(lane)
    prettyprint(lane3)
    assert lane == lane2
    assert lane != lane3
    assert (
        version_validation(
            "t_road_lanes_laneSection_left_lane", lane, wanted_schema="xodr"
        )
        == ValidationResponse.OK
    )


def test_lanesection():
    ls = xodr.LaneSection(0, xodr.Lane())
    prettyprint(ls.get_element())
    right_lane = xodr.Lane()
    ls.add_right_lane(right_lane)
    prettyprint(ls.get_element())
    left_lane = xodr.Lane(a=2)
    ls.add_left_lane(left_lane)
    prettyprint(ls.get_element())

    ls2 = xodr.LaneSection(0, xodr.Lane())
    ls2.add_right_lane(xodr.Lane())
    ls2.add_left_lane(xodr.Lane(a=2))
    prettyprint(ls2.get_element())
    ls3 = xodr.LaneSection(0, xodr.Lane())
    ls3.add_right_lane(xodr.Lane(b=2))
    ls3.add_left_lane(xodr.Lane(a=2))

    assert ls == ls2
    assert ls != ls3
    assert (
        version_validation("t_road_lanes_laneSection", ls, wanted_schema="xodr")
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        xodr.LaneSection(0, "dummy")
    with pytest.raises(TypeError):
        ls.add_left_lane("dummy")
    with pytest.raises(TypeError):
        ls.add_right_lane("dummy")


def test_laneoffset():
    laneoffset1 = xodr.LaneOffset(0, 1, 2, 3, 4)
    prettyprint(laneoffset1.get_element())
    laneoffset2 = xodr.LaneOffset(5, 6, 7, 8, 9)
    prettyprint(laneoffset2.get_element())
    laneoffset3 = xodr.LaneOffset(0, 1, 2, 3, 4)
    assert laneoffset1 != laneoffset2
    assert laneoffset1 == laneoffset3
    assert (
        version_validation("t_road_lanes_laneOffset", laneoffset1, wanted_schema="xodr")
        == ValidationResponse.OK
    )


def test_lane_width_calc():
    lane = xodr.Lane(a=3, b=2)
    lane.add_lane_width(a=2, b=0.5, soffset=10)
    assert lane.get_width(5) == 13
    assert lane.get_width(12) == 3


def test_lanes():
    ls = xodr.LaneSection(0, xodr.Lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)
    lanes.add_laneoffset(xodr.LaneOffset(0, 1, 2, 3, 4))
    prettyprint(lanes.get_element())

    ls2 = xodr.LaneSection(0, xodr.Lane())
    lanes2 = xodr.Lanes()
    lanes2.add_lanesection(ls2)
    lanes2.add_laneoffset(xodr.LaneOffset(0, 1, 2, 3, 4))

    ls3 = xodr.LaneSection(0, xodr.Lane())
    lanes3 = xodr.Lanes()
    lanes3.add_lanesection(ls3)
    lanes3.add_laneoffset(xodr.LaneOffset(0, 2, 2, 3, 4))
    lanes3.add_userdata(xodr.UserData("stuffs", "valuestuffs"))
    assert lanes == lanes2
    assert lanes != lanes3
    assert (
        version_validation("t_road_lanes", lanes, wanted_schema="xodr")
        == ValidationResponse.OK
    )
    with pytest.raises(TypeError):
        lanes.add_laneoffset("dummy")
    with pytest.raises(TypeError):
        lanes.add_lanesection("dummy")


## tests for adjusting roadmarks


def create_new_lane():
    lane = xodr.Lane()
    lane.add_roadmark(xodr.std_roadmark_broken_tight())
    return lane


def test_adjust_lanes_one_lanesection_no_connection():
    ls = xodr.LaneSection(0, create_new_lane())
    ls.add_left_lane(create_new_lane())
    ls.add_right_lane(create_new_lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)

    lanes.adjust_road_marks_from_start(11)
    assert ls.rightlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls.rightlanes[0].roadmark[0]._line[0].soffset == 0
    assert ls.leftlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls.leftlanes[0].roadmark[0]._line[0].soffset == 0
    assert ls.centerlane.roadmark[0]._line[0]._remainder == 2
    assert ls.centerlane.roadmark[0]._line[0].soffset == 0


def test_adjust_lanes_one_lanesection_end_connection():
    ls = xodr.LaneSection(0, create_new_lane())
    ls.add_left_lane(create_new_lane())
    ls.add_right_lane(create_new_lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)

    connecting_lane_section = xodr.LaneSection(0, create_new_lane())
    connecting_lane_section.add_left_lane(create_new_lane())
    connecting_lane_section.add_right_lane(create_new_lane())

    connecting_lanes = xodr.Lanes()
    connecting_lanes.add_lanesection(connecting_lane_section)
    connecting_lanes.adjust_road_marks_from_start(10)

    lanes.adjust_road_marks_from_start(
        11, connecting_lane_section, xodr.ContactPoint.end
    )

    assert ls.rightlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls.rightlanes[0].roadmark[0]._line[0]._remainder == 0
    assert ls.leftlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls.leftlanes[0].roadmark[0]._line[0]._remainder == 0
    assert ls.centerlane.roadmark[0]._line[0].soffset == 2
    assert ls.centerlane.roadmark[0]._line[0]._remainder == 0


def test_adjust_lanes_one_lanesection_start_connection():
    ls = xodr.LaneSection(0, create_new_lane())
    ls.add_left_lane(create_new_lane())
    ls.add_right_lane(create_new_lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)

    connecting_lane_section = xodr.LaneSection(0, create_new_lane())
    connecting_lane_section.add_left_lane(create_new_lane())
    connecting_lane_section.add_right_lane(create_new_lane())

    connecting_lanes = xodr.Lanes()
    connecting_lanes.add_lanesection(connecting_lane_section)
    connecting_lanes.adjust_road_marks_from_start(11)

    lanes.adjust_road_marks_from_start(
        13, connecting_lane_section, xodr.ContactPoint.start
    )

    assert ls.rightlanes[0].roadmark[0]._line[0].soffset == 3
    assert ls.rightlanes[0].roadmark[0]._line[0]._remainder == 1
    assert ls.leftlanes[0].roadmark[0]._line[0].soffset == 3
    assert ls.leftlanes[0].roadmark[0]._line[0]._remainder == 1
    assert ls.centerlane.roadmark[0]._line[0].soffset == 3
    assert ls.centerlane.roadmark[0]._line[0]._remainder == 1


def test_adjust_lanes_multi_lanesection_no_connection():
    ls1 = xodr.LaneSection(0, create_new_lane())
    ls1.add_left_lane(create_new_lane())
    ls1.add_right_lane(create_new_lane())

    ls2 = xodr.LaneSection(10, create_new_lane())
    ls2.add_left_lane(create_new_lane())
    ls2.add_right_lane(create_new_lane())

    ls3 = xodr.LaneSection(22, create_new_lane())
    ls3.add_left_lane(create_new_lane())
    ls3.add_right_lane(create_new_lane())

    lanes = xodr.Lanes()
    lanes.add_lanesection(ls1)
    lanes.add_lanesection(ls2)
    lanes.add_lanesection(ls3)

    lanes.adjust_road_marks_from_start(30)

    assert ls1.rightlanes[0].roadmark[0]._line[0].soffset == 0
    assert ls1.rightlanes[0].roadmark[0]._line[0]._remainder == 1
    assert ls2.rightlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls2.rightlanes[0].roadmark[0]._line[0]._remainder == 1
    assert ls3.rightlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls3.rightlanes[0].roadmark[0]._line[0]._remainder == 3

    assert ls1.leftlanes[0].roadmark[0]._line[0].soffset == 0
    assert ls1.leftlanes[0].roadmark[0]._line[0]._remainder == 1
    assert ls2.leftlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls2.leftlanes[0].roadmark[0]._line[0]._remainder == 1
    assert ls3.leftlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls3.leftlanes[0].roadmark[0]._line[0]._remainder == 3

    assert ls1.centerlane.roadmark[0]._line[0].soffset == 0
    assert ls1.centerlane.roadmark[0]._line[0]._remainder == 1
    assert ls2.centerlane.roadmark[0]._line[0].soffset == 2
    assert ls2.centerlane.roadmark[0]._line[0]._remainder == 1
    assert ls3.centerlane.roadmark[0]._line[0].soffset == 2
    assert ls3.centerlane.roadmark[0]._line[0]._remainder == 3


def test_adjust_lanes_end_one_lanesection_no_connection():
    ls = xodr.LaneSection(0, create_new_lane())
    ls.add_left_lane(create_new_lane())
    ls.add_right_lane(create_new_lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)

    lanes.adjust_road_marks_from_end(11)
    assert ls.rightlanes[0].roadmark[0]._line[0]._remainder == 0
    assert ls.rightlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls.leftlanes[0].roadmark[0]._line[0]._remainder == 0
    assert ls.leftlanes[0].roadmark[0]._line[0].soffset == 2
    assert ls.centerlane.roadmark[0]._line[0]._remainder == 0
    assert ls.centerlane.roadmark[0]._line[0].soffset == 2


def test_adjust_lanes_end_one_lanesection_end_connection():
    ls = xodr.LaneSection(0, create_new_lane())
    ls.add_left_lane(create_new_lane())
    ls.add_right_lane(create_new_lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)

    connecting_lane_section = xodr.LaneSection(0, create_new_lane())
    connecting_lane_section.add_left_lane(create_new_lane())
    connecting_lane_section.add_right_lane(create_new_lane())

    connecting_lanes = xodr.Lanes()
    connecting_lanes.add_lanesection(connecting_lane_section)
    connecting_lanes.adjust_road_marks_from_start(10)

    lanes.adjust_road_marks_from_end(11, connecting_lane_section, xodr.ContactPoint.end)

    assert ls.rightlanes[0].roadmark[0]._line[0].soffset == 0
    assert ls.rightlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls.leftlanes[0].roadmark[0]._line[0].soffset == 0
    assert ls.leftlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls.centerlane.roadmark[0]._line[0].soffset == 0
    assert ls.centerlane.roadmark[0]._line[0]._remainder == 2


def test_adjust_lanes_end_one_lanesection_start_connection():
    ls = xodr.LaneSection(0, create_new_lane())
    ls.add_left_lane(create_new_lane())
    ls.add_right_lane(create_new_lane())
    lanes = xodr.Lanes()
    lanes.add_lanesection(ls)

    connecting_lane_section = xodr.LaneSection(0, create_new_lane())
    connecting_lane_section.add_left_lane(create_new_lane())
    connecting_lane_section.add_right_lane(create_new_lane())

    connecting_lanes = xodr.Lanes()
    connecting_lanes.add_lanesection(connecting_lane_section)
    connecting_lanes.adjust_road_marks_from_start(11)

    lanes.adjust_road_marks_from_end(
        13, connecting_lane_section, xodr.ContactPoint.start
    )

    assert ls.rightlanes[0].roadmark[0]._line[0].soffset == 1
    assert ls.rightlanes[0].roadmark[0]._line[0]._remainder == 3
    assert ls.leftlanes[0].roadmark[0]._line[0].soffset == 1
    assert ls.leftlanes[0].roadmark[0]._line[0]._remainder == 3
    assert ls.centerlane.roadmark[0]._line[0].soffset == 1
    assert ls.centerlane.roadmark[0]._line[0]._remainder == 3


def test_adjust_lanes_end_multi_lanesection_no_connection():
    ls1 = xodr.LaneSection(0, create_new_lane())
    ls1.add_left_lane(create_new_lane())
    ls1.add_right_lane(create_new_lane())

    ls2 = xodr.LaneSection(8, create_new_lane())
    ls2.add_left_lane(create_new_lane())
    ls2.add_right_lane(create_new_lane())

    ls3 = xodr.LaneSection(20, create_new_lane())
    ls3.add_left_lane(create_new_lane())
    ls3.add_right_lane(create_new_lane())

    lanes = xodr.Lanes()
    lanes.add_lanesection(ls1)
    lanes.add_lanesection(ls2)
    lanes.add_lanesection(ls3)

    lanes.adjust_road_marks_from_end(30)

    assert ls1.rightlanes[0].roadmark[0]._line[0].soffset == 3
    assert ls1.rightlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls2.rightlanes[0].roadmark[0]._line[0].soffset == 1
    assert ls2.rightlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls3.rightlanes[0].roadmark[0]._line[0].soffset == 1
    assert ls3.rightlanes[0].roadmark[0]._line[0]._remainder == 0

    assert ls1.leftlanes[0].roadmark[0]._line[0].soffset == 3
    assert ls1.leftlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls2.leftlanes[0].roadmark[0]._line[0].soffset == 1
    assert ls2.leftlanes[0].roadmark[0]._line[0]._remainder == 2
    assert ls3.leftlanes[0].roadmark[0]._line[0].soffset == 1
    assert ls3.leftlanes[0].roadmark[0]._line[0]._remainder == 0

    assert ls1.centerlane.roadmark[0]._line[0].soffset == 3
    assert ls1.centerlane.roadmark[0]._line[0]._remainder == 2
    assert ls2.centerlane.roadmark[0]._line[0].soffset == 1
    assert ls2.centerlane.roadmark[0]._line[0]._remainder == 2
    assert ls3.centerlane.roadmark[0]._line[0].soffset == 1
    assert ls3.centerlane.roadmark[0]._line[0]._remainder == 0
