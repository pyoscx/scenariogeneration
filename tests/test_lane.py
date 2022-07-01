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
from scenariogeneration.xodr.generators import STD_ROADMARK_BROKEN, STD_ROADMARK_SOLID


def test_roadline():
    line = pyodrx.RoadLine()

    prettyprint(line.get_element())
    line = pyodrx.RoadLine(
        1, 2, 3, 5, 1, pyodrx.MarkRule.no_passing, pyodrx.RoadMarkColor.standard
    )
    prettyprint(line.get_element())
    line2 = pyodrx.RoadLine(
        1, 2, 3, 5, 1, pyodrx.MarkRule.no_passing, pyodrx.RoadMarkColor.standard
    )
    line3 = pyodrx.RoadLine(
        1, 2, 3, 5, 1, pyodrx.MarkRule.none, pyodrx.RoadMarkColor.standard
    )
    assert line == line2
    assert line != line3


def test_roadmark():
    mark = pyodrx.RoadMark(pyodrx.RoadMarkType.solid, 0.2)
    prettyprint(mark.get_element())
    mark = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid,
        0.2,
        1,
        1,
        1,
        pyodrx.MarkRule.no_passing,
        pyodrx.RoadMarkColor.standard,
    )
    prettyprint(mark.get_element())
    mark2 = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid,
        0.2,
        1,
        1,
        1,
        pyodrx.MarkRule.no_passing,
        pyodrx.RoadMarkColor.standard,
    )
    mark3 = pyodrx.RoadMark(
        pyodrx.RoadMarkType.solid,
        0.2,
        1,
        1,
        2,
        pyodrx.MarkRule.no_passing,
        pyodrx.RoadMarkColor.standard,
    )
    assert mark == mark2
    assert mark != mark3

    mark4 = pyodrx.RoadMark(pyodrx.RoadMarkType.solid_solid)
    mark4.add_specific_road_line(pyodrx.RoadLine(0.2, 0, 0, 0.2, 0))
    mark4.add_specific_road_line(pyodrx.RoadLine(0.2, 0, 0, 0.2, 0))
    prettyprint(mark4.get_element())


def test_poly3struct():
    ps1 = pyodrx.lane._poly3struct(1, 2, 3, 4, 5)
    ps2 = pyodrx.lane._poly3struct(1, 2, 3, 4, 5)
    ps3 = pyodrx.lane._poly3struct(2, 2, 3, 4, 5)
    assert ps1 == ps2
    assert ps1 != ps3


def test_lane():
    lane = pyodrx.Lane()
    lane._set_lane_id(1)
    prettyprint(lane.get_element())
    lane = pyodrx.Lane(pyodrx.LaneType.driving, 1, 1, 1, 1, 2)
    lane._set_lane_id(1)
    prettyprint(lane.get_element())

    lane2 = pyodrx.Lane(pyodrx.LaneType.driving, 1, 1, 1, 1, 2)
    lane2._set_lane_id(1)
    lane3 = pyodrx.Lane(pyodrx.LaneType.driving, 1, 1, 1, 3, 2)
    lane3._set_lane_id(1)
    assert lane == lane2
    assert lane != lane3


def test_lane_with_multiple_widths():
    lane = pyodrx.Lane()
    lane._set_lane_id(1)
    prettyprint(lane.get_element())
    lane = pyodrx.Lane(pyodrx.LaneType.driving, 1, 1, 1, 1, 2)
    lane.add_lane_width(1, 2, 3, 4, 5)

    lane._set_lane_id(1)
    prettyprint(lane.get_element())

    lane2 = pyodrx.Lane(pyodrx.LaneType.driving, 1, 1, 1, 1, 2)
    lane2._set_lane_id(1)
    lane2.add_lane_width(1, 2, 3, 4, 5)
    lane3 = pyodrx.Lane(pyodrx.LaneType.driving, 1, 1, 1, 3, 2)
    lane3._set_lane_id(1)
    lane3.add_lane_width(1, 2, 3, 4, 6)

    assert lane == lane2
    assert lane != lane3


def test_lane_with_height():
    lane = pyodrx.Lane(pyodrx.LaneType.sidewalk, 1, 1, 1, 1, 2)
    lane._set_lane_id(1)
    lane.add_height(0.15)
    prettyprint(lane.get_element())


def test_lane_with_roadmarks():
    lane = pyodrx.Lane()
    lane._set_lane_id(1)
    lane.add_roadmark(STD_ROADMARK_BROKEN)
    lane2 = pyodrx.Lane()
    lane2._set_lane_id(1)
    lane2.add_roadmark(STD_ROADMARK_BROKEN)
    lane3 = pyodrx.Lane()
    lane3._set_lane_id(1)
    lane3.add_roadmark(STD_ROADMARK_BROKEN)
    lane3.add_roadmark(STD_ROADMARK_SOLID)
    prettyprint(lane)
    prettyprint(lane3)
    assert lane == lane2
    assert lane != lane3


def test_lanesection():

    ls = pyodrx.LaneSection(0, pyodrx.Lane())
    prettyprint(ls.get_element())
    right_lane = pyodrx.Lane()
    ls.add_right_lane(right_lane)
    prettyprint(ls.get_element())
    left_lane = pyodrx.Lane(a=2)
    ls.add_left_lane(left_lane)
    prettyprint(ls.get_element())

    ls2 = pyodrx.LaneSection(0, pyodrx.Lane())
    ls2.add_right_lane(pyodrx.Lane())
    ls2.add_left_lane(pyodrx.Lane(a=2))
    prettyprint(ls2.get_element())
    ls3 = pyodrx.LaneSection(0, pyodrx.Lane())
    ls3.add_right_lane(pyodrx.Lane(b=2))
    ls3.add_left_lane(pyodrx.Lane(a=2))

    assert ls == ls2
    assert ls != ls3


def test_laneoffset():
    laneoffset1 = pyodrx.LaneOffset(0, 1, 2, 3, 4)
    prettyprint(laneoffset1.get_element())
    laneoffset2 = pyodrx.LaneOffset(5, 6, 7, 8, 9)
    prettyprint(laneoffset2.get_element())
    laneoffset3 = pyodrx.LaneOffset(0, 1, 2, 3, 4)
    assert laneoffset1 != laneoffset2
    assert laneoffset1 == laneoffset3


def test_lane_width_calc():
    lane = pyodrx.Lane(a=3, b=2)
    lane.add_lane_width(a=2, b=0.5, soffset=10)
    assert lane.get_width(5) == 13
    assert lane.get_width(12) == 3


def test_lanes():

    ls = pyodrx.LaneSection(0, pyodrx.Lane())
    lanes = pyodrx.Lanes()
    lanes.add_lanesection(ls)
    lanes.add_laneoffset(pyodrx.LaneOffset(0, 1, 2, 3, 4))
    prettyprint(lanes.get_element())

    ls2 = pyodrx.LaneSection(0, pyodrx.Lane())
    lanes2 = pyodrx.Lanes()
    lanes2.add_lanesection(ls2)
    lanes2.add_laneoffset(pyodrx.LaneOffset(0, 1, 2, 3, 4))

    ls3 = pyodrx.LaneSection(0, pyodrx.Lane())
    lanes3 = pyodrx.Lanes()
    lanes3.add_lanesection(ls3)
    lanes3.add_laneoffset(pyodrx.LaneOffset(0, 2, 2, 3, 4))
    assert lanes == lanes2
    assert lanes != lanes3
