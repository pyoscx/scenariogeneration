from scenariogeneration import xodr, prettyprint


def test_create_lane_lists_only_int():
    right_lanes, left_lanes = xodr.lane_def._create_lane_lists(3, 3, 100, 3)
    assert len(right_lanes) == 1
    assert len(left_lanes) == 1
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 100
    assert left_lanes[0].s_end == 100
    assert right_lanes[0].lane_start_widths == [3, 3, 3]
    assert left_lanes[0].lane_start_widths == [3, 3, 3]


def test_create_lane_lists_only_left():
    right_lanes, left_lanes = xodr.lane_def._create_lane_lists(0, 3, 100, 3)
    assert len(right_lanes) == 1
    assert len(left_lanes) == 1
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 100
    assert left_lanes[0].s_end == 100
    assert right_lanes[0].lane_start_widths == []
    assert left_lanes[0].lane_start_widths == [3, 3, 3]


def test_create_lane_lists_only_right():
    right_lanes, left_lanes = xodr.lane_def._create_lane_lists(3, 0, 100, 3)
    assert len(right_lanes) == 1
    assert len(left_lanes) == 1
    assert right_lanes[0].s_start == 0
    assert left_lanes[0].s_start == 0
    assert right_lanes[0].s_end == 100
    assert left_lanes[0].s_end == 100
    assert right_lanes[0].lane_start_widths == [3, 3, 3]
    assert left_lanes[0].lane_start_widths == []


def test_create_lane_lists_lane_def_no_widths_right():
    right_lanes, left_lanes = xodr.lane_def._create_lane_lists(
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
    right_lanes, left_lanes = xodr.lane_def._create_lane_lists(
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
