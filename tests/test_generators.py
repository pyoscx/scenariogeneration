"""
  scenariogeneration
  https://github.com/pyoscx/scenariogeneration

  This Source Code Form is subject to the terms of the Mozilla Public
  License, v. 2.0. If a copy of the MPL was not distributed with this
  file, You can obtain one at https://mozilla.org/MPL/2.0/.

  Copyright (c) 2022 The scenariogeneration Authors.

"""
import pytest


from scenariogeneration import xodr, prettyprint


def test_create_lane_lists_only_int():
    right_lanes, left_lanes = xodr.generators._create_lane_lists(3, 3, 100, 3)
    assert len(right_lanes) == 1
    assert len(left_lanes) == 1
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 100
    assert left_lanes[0].s_end == 100
    assert right_lanes[0].lane_start_widths == [3, 3, 3]
    assert left_lanes[0].lane_start_widths == [3, 3, 3]


def test_create_lane_lists_only_left():
    right_lanes, left_lanes = xodr.generators._create_lane_lists(0, 3, 100, 3)
    assert len(right_lanes) == 1
    assert len(left_lanes) == 1
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 100
    assert left_lanes[0].s_end == 100
    assert right_lanes[0].lane_start_widths == []
    assert left_lanes[0].lane_start_widths == [3, 3, 3]


def test_create_lane_lists_only_right():
    right_lanes, left_lanes = xodr.generators._create_lane_lists(3, 0, 100, 3)
    assert len(right_lanes) == 1
    assert len(left_lanes) == 1
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 100
    assert left_lanes[0].s_end == 100
    assert right_lanes[0].lane_start_widths == [3, 3, 3]
    assert left_lanes[0].lane_start_widths == []


def test_create_lane_lists_lane_def_no_widths_right():
    right_lanes, left_lanes = xodr.generators._create_lane_lists(
        [xodr.LaneDef(10, 90, 3, 4, 2)], 3, 100, 3
    )
    assert len(right_lanes) == 3
    assert len(left_lanes) == 3
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 10
    assert left_lanes[0].s_end == 10
    assert right_lanes[0].lane_start_widths == [3, 3, 3]
    assert left_lanes[0].lane_start_widths == [3, 3, 3]

    assert right_lanes[1].s_start == 10
    assert left_lanes[1].s_start == 10
    assert right_lanes[1].s_end == 90
    assert left_lanes[1].s_end == 90
    assert right_lanes[1].lane_start_widths == [3, 0, 3, 3]
    assert right_lanes[1].lane_end_widths == [3, 3, 3, 3]
    assert left_lanes[1].lane_start_widths == [3, 3, 3]

    assert right_lanes[2].s_start == 90
    assert left_lanes[2].s_start == 90
    assert right_lanes[2].s_end == 100
    assert left_lanes[2].s_end == 100
    assert right_lanes[2].lane_start_widths == [3, 3, 3, 3]
    assert right_lanes[2].lane_end_widths == [3, 3, 3, 3]
    assert left_lanes[2].lane_start_widths == [3, 3, 3]


def test_create_lane_lists_lane_def_no_widths_left():
    right_lanes, left_lanes = xodr.generators._create_lane_lists(
        3, [xodr.LaneDef(10, 90, 3, 4, 2)], 100, 3
    )
    assert len(right_lanes) == 3
    assert len(left_lanes) == 3
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 10
    assert left_lanes[0].s_end == 10
    assert right_lanes[0].lane_start_widths == [3, 3, 3]
    assert left_lanes[0].lane_start_widths == [3, 3, 3]

    assert right_lanes[1].s_start == 10
    assert left_lanes[1].s_start == 10
    assert right_lanes[1].s_end == 90
    assert left_lanes[1].s_end == 90
    assert left_lanes[1].lane_start_widths == [3, 0, 3, 3]
    assert left_lanes[1].lane_end_widths == [3, 3, 3, 3]
    assert right_lanes[1].lane_start_widths == [3, 3, 3]


def test_create_left_lane_split_first_lane():
    lanedef = xodr.LaneDef(10, 20, 1, 2, 1)
    lanes = xodr.create_lanes_merge_split(
        0, [lanedef], 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert (
        lanes.lanesections[0].centerlane.roadmark[0].marking_type
        == xodr.RoadMarkType.solid_solid
    )
    assert (
        lanes.lanesections[1].centerlane.roadmark[0].marking_type
        == xodr.RoadMarkType.solid_solid
    )
    assert (
        lanes.lanesections[2].centerlane.roadmark[0].marking_type
        == xodr.RoadMarkType.solid_solid
    )
    assert len(lanes.lanesections[0].rightlanes) == 0
    assert len(lanes.lanesections[1].rightlanes) == 0
    assert len(lanes.lanesections[2].rightlanes) == 0

    assert len(lanes.lanesections[0].leftlanes) == 1
    assert len(lanes.lanesections[1].leftlanes) == 2
    assert len(lanes.lanesections[2].leftlanes) == 2

    ## check some lane properties
    assert (
        lanes.lanesections[0].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].leftlanes[0].widths[0].a == 0
    assert lanes.lanesections[1].leftlanes[0].widths[0].c != 0
    assert (
        lanes.lanesections[1].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[1].leftlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[2].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[2].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].leftlanes[0].widths[0].c == 0
    assert lanes.lanesections[2].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[2].leftlanes[1].widths[0].c == 0


def test_create_left_lane_split_second_lane():
    lanedef = xodr.LaneDef(10, 20, 1, 2, 2)
    lanes = xodr.create_lanes_merge_split(
        0, [lanedef], 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].rightlanes) == 0
    assert len(lanes.lanesections[1].rightlanes) == 0
    assert len(lanes.lanesections[2].rightlanes) == 0

    assert len(lanes.lanesections[0].leftlanes) == 1
    assert len(lanes.lanesections[1].leftlanes) == 2
    assert len(lanes.lanesections[2].leftlanes) == 2

    ## check some lane properties
    assert (
        lanes.lanesections[0].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].leftlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].leftlanes[1].widths[0].a == 0
    assert lanes.lanesections[1].leftlanes[1].widths[0].c != 0

    assert (
        lanes.lanesections[2].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[2].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].leftlanes[0].widths[0].c == 0
    assert lanes.lanesections[2].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[2].leftlanes[1].widths[0].c == 0


def test_create_right_lane_split_first_lane():
    lanedef = xodr.LaneDef(10, 20, 1, 2, 1)
    lanes = xodr.create_lanes_merge_split(
        [lanedef], 0, 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].leftlanes) == 0
    assert len(lanes.lanesections[1].leftlanes) == 0
    assert len(lanes.lanesections[2].leftlanes) == 0

    assert len(lanes.lanesections[0].rightlanes) == 1
    assert len(lanes.lanesections[1].rightlanes) == 2
    assert len(lanes.lanesections[2].rightlanes) == 2

    ## check some lane properties
    assert (
        lanes.lanesections[0].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].rightlanes[0].widths[0].a == 0
    assert lanes.lanesections[1].rightlanes[0].widths[0].c != 0
    assert (
        lanes.lanesections[1].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[2].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[2].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[2].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[1].widths[0].c == 0


def test_create_right_lane_split_second_lane():
    lanedef = xodr.LaneDef(10, 20, 1, 2, 2)
    lanes = xodr.create_lanes_merge_split(
        [lanedef], 0, 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].leftlanes) == 0
    assert len(lanes.lanesections[1].leftlanes) == 0
    assert len(lanes.lanesections[2].leftlanes) == 0

    assert len(lanes.lanesections[0].rightlanes) == 1
    assert len(lanes.lanesections[1].rightlanes) == 2
    assert len(lanes.lanesections[2].rightlanes) == 2

    ## check some lane properties
    assert (
        lanes.lanesections[0].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].rightlanes[1].widths[0].a == 0
    assert lanes.lanesections[1].rightlanes[1].widths[0].c != 0
    assert (
        lanes.lanesections[2].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[2].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[2].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[1].widths[0].c == 0


def test_create_left_lane_merge_first_lane():
    lanedef = xodr.LaneDef(10, 20, 2, 1, 1)
    lanes = xodr.create_lanes_merge_split(
        0, [lanedef], 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].rightlanes) == 0
    assert len(lanes.lanesections[1].rightlanes) == 0
    assert len(lanes.lanesections[2].rightlanes) == 0

    assert len(lanes.lanesections[0].leftlanes) == 2
    assert len(lanes.lanesections[1].leftlanes) == 2
    assert len(lanes.lanesections[2].leftlanes) == 1

    ## check some lane properties
    assert (
        lanes.lanesections[0].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[0].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[0].widths[0].c == 0
    assert lanes.lanesections[0].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[1].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].leftlanes[0].widths[0].c != 0
    assert (
        lanes.lanesections[1].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[1].leftlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[2].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].leftlanes[0].widths[0].c == 0


def test_create_left_lane_merge_second_lane():
    lanedef = xodr.LaneDef(10, 20, 2, 1, 2)
    lanes = xodr.create_lanes_merge_split(
        0, [lanedef], 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].rightlanes) == 0
    assert len(lanes.lanesections[1].rightlanes) == 0
    assert len(lanes.lanesections[2].rightlanes) == 0

    assert len(lanes.lanesections[0].leftlanes) == 2
    assert len(lanes.lanesections[1].leftlanes) == 2
    assert len(lanes.lanesections[2].leftlanes) == 1

    ## check some lane properties
    assert (
        lanes.lanesections[0].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[0].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[0].widths[0].c == 0
    assert lanes.lanesections[0].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[1].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].leftlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].leftlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].leftlanes[1].widths[0].a == 3
    assert lanes.lanesections[1].leftlanes[1].widths[0].c != 0
    assert (
        lanes.lanesections[2].leftlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].leftlanes[0].widths[0].c == 0


def test_create_right_lane_merge_first_lane():
    lanedef = xodr.LaneDef(10, 20, 2, 1, -1)
    lanes = xodr.create_lanes_merge_split(
        [lanedef], 0, 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].leftlanes) == 0
    assert len(lanes.lanesections[1].leftlanes) == 0
    assert len(lanes.lanesections[2].leftlanes) == 0

    assert len(lanes.lanesections[0].rightlanes) == 2
    assert len(lanes.lanesections[1].rightlanes) == 2
    assert len(lanes.lanesections[2].rightlanes) == 1

    ## check some lane properties
    assert (
        lanes.lanesections[0].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[0].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[0].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[1].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[0].widths[0].c != 0
    assert (
        lanes.lanesections[1].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[2].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[0].widths[0].c == 0


def test_create_right_lane_merge_second_lane():
    lanedef = xodr.LaneDef(10, 20, 2, 1, 2)
    lanes = xodr.create_lanes_merge_split(
        [lanedef], 0, 30, xodr.std_roadmark_solid_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3
    assert lanes.lanesections[0].s == 0
    assert lanes.lanesections[1].s == 10
    assert lanes.lanesections[2].s == 20

    assert len(lanes.lanesections[0].leftlanes) == 0
    assert len(lanes.lanesections[1].leftlanes) == 0
    assert len(lanes.lanesections[2].leftlanes) == 0

    assert len(lanes.lanesections[0].rightlanes) == 2
    assert len(lanes.lanesections[1].rightlanes) == 2
    assert len(lanes.lanesections[2].rightlanes) == 1

    ## check some lane properties
    assert (
        lanes.lanesections[0].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert (
        lanes.lanesections[0].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[0].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[0].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[1].widths[0].c == 0
    assert (
        lanes.lanesections[1].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.broken
    )
    assert lanes.lanesections[1].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[0].widths[0].c == 0
    assert (
        lanes.lanesections[1].rightlanes[1].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[1].rightlanes[1].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[1].widths[0].c != 0
    assert (
        lanes.lanesections[2].rightlanes[0].roadmark[0].marking_type
        == xodr.RoadMarkType.solid
    )
    assert lanes.lanesections[2].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[0].widths[0].c == 0


def test_create_lanes_with_uniform_lane_width_diff():
    lanes = xodr.create_lanes_merge_split(1, 1, 30, xodr.std_roadmark_solid(), 3, 4)
    assert len(lanes.lanesections) == 1
    assert len(lanes.lanesections[0].leftlanes) == 1
    assert len(lanes.lanesections[0].rightlanes) == 1
    assert lanes.lanesections[0].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].leftlanes[0].widths[0].c != 0
    assert lanes.lanesections[0].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[0].widths[0].c != 0


def test_create_lanes_with_lane_width_change_in_middle():
    lanedef_right = xodr.LaneDef(10, 20, 2, 2, None, [4, 5], [3, 4])
    lanedef_left = xodr.LaneDef(10, 20, 2, 2, None, [3, 4], [4, 5])
    lanes = xodr.create_lanes_merge_split(
        [lanedef_right], [lanedef_left], 30, xodr.std_roadmark_solid(), 3, 3
    )
    assert len(lanes.lanesections) == 3

    assert len(lanes.lanesections[0].leftlanes) == 2
    assert len(lanes.lanesections[0].rightlanes) == 2

    assert lanes.lanesections[0].rightlanes[0].widths[0].a == 4
    assert lanes.lanesections[0].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[0].rightlanes[1].widths[0].a == 5
    assert lanes.lanesections[0].rightlanes[1].widths[0].c == 0
    assert lanes.lanesections[0].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[0].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[0].leftlanes[1].widths[0].a == 4
    assert lanes.lanesections[0].rightlanes[1].widths[0].c == 0

    assert lanes.lanesections[1].rightlanes[0].widths[0].a == 4
    assert lanes.lanesections[1].rightlanes[0].widths[0].c != 0
    assert lanes.lanesections[1].rightlanes[1].widths[0].a == 5
    assert lanes.lanesections[1].rightlanes[1].widths[0].c != 0
    assert lanes.lanesections[1].leftlanes[0].widths[0].a == 3
    assert lanes.lanesections[1].rightlanes[0].widths[0].c != 0
    assert lanes.lanesections[1].leftlanes[1].widths[0].a == 4
    assert lanes.lanesections[1].rightlanes[1].widths[0].c != 0

    assert lanes.lanesections[2].rightlanes[0].widths[0].a == 3
    assert lanes.lanesections[2].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[2].rightlanes[1].widths[0].a == 4
    assert lanes.lanesections[2].rightlanes[1].widths[0].c == 0
    assert lanes.lanesections[2].leftlanes[0].widths[0].a == 4
    assert lanes.lanesections[2].rightlanes[0].widths[0].c == 0
    assert lanes.lanesections[2].leftlanes[1].widths[0].a == 5
    assert lanes.lanesections[2].rightlanes[1].widths[0].c == 0
