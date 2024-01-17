import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint
import numpy as np


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", -1, -1]),
        (["successor", "predecessor", -1, -1]),
        (["successor", "successor", -1, 1]),
        (["predecessor", "predecessor", -1, 1]),
    ],
)
def test_connection_single_right_lane_to_dobule_lane(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=0, right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", 1, 1]),
        (["successor", "predecessor", 1, 1]),
        (["successor", "successor", 1, -1]),
        (["predecessor", "predecessor", 1, -1]),
    ],
)
def test_connections_single_left_lane_to_double(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=1, right_lanes=0)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", 1, 1]),
        (["successor", "predecessor", 1, 1]),
        (["successor", "successor", -1, 1]),
        (["predecessor", "predecessor", -1, 1]),
    ],
)
def test_connections_double_to_single_left_lane(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=1, right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=0)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", -1, -1]),
        (["successor", "predecessor", -1, -1]),
        (["successor", "successor", -1, 1]),
        (["predecessor", "predecessor", -1, 1]),
    ],
)
def test_connections_double_to_single_right_lane(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=0, right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", 1, 1]),
        (["successor", "predecessor", 1, 1]),
        (["successor", "successor", 1, -1]),
        (["predecessor", "predecessor", 1, -1]),
    ],
)
def test_connections_single_left_lane_to_double(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=1, right_lanes=0)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", 1, 1]),
        (["successor", "predecessor", 1, 1]),
        (["successor", "successor", -1, 1]),
        (["predecessor", "predecessor", -1, 1]),
    ],
)
def test_connections_double_to_single_left_lane(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=1, right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=0)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", -1, -1]),
        (["successor", "predecessor", -1, -1]),
        (["successor", "successor", -1, 1]),
        (["predecessor", "predecessor", -1, 1]),
    ],
)
def test_connections_double_to_single_right_lane(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=0, right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", [1, -1], [1, -1]]),
        (["successor", "predecessor", [1, -1], [1, -1]]),
        (["successor", "successor", [1, -1], [-1, 1]]),
        (["predecessor", "predecessor", [1, -1], [-1, 1]]),
    ],
)
def test_connections_left_and_right(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=1, right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=1, right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(
        road1, 20, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_circular_geometry(
        road2, 20, 3, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes == data[2]
    assert r2_lanes == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes == data[3]
    assert r2_lanes == data[2]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", "successor", [1, 2, -1, -2], [1, 2, -1, -2]]),
        (["successor", "predecessor", [1, 2, -1, -2], [1, 2, -1, -2]]),
        (["successor", "successor", [1, 2, -1, -2], [-1, -2, 1, 2]]),
        (["predecessor", "predecessor", [1, 2, -1, -2], [-1, -2, 1, 2]]),
    ],
)
def test_connections_4lanes(data):
    junction_creator = xodr.CommonJunctionCreator(
        id=100, name="my_junction", startnum=100
    )
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01, 100), 2, left_lanes=2, right_lanes=2)

    junction_creator.add_incoming_road_cartesian_geometry(
        road1, -20, 0, 0, road_connection=data[0]
    )
    junction_creator.add_incoming_road_cartesian_geometry(
        road2, 20, 0, np.pi, road_connection=data[1]
    )

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1, road2)
    assert r1_lanes == data[2]
    assert r2_lanes == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2, road1)
    assert r1_lanes == data[3]
    assert r2_lanes == data[2]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", xodr.ContactPoint.start]),
        (["successor", xodr.ContactPoint.end]),
    ],
)
def test_contact_point_getter(data):
    jc = xodr.CommonJunctionCreator(100, "my_junction")
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, data[0])
    jc._get_contact_point_connecting_road(1) == data[1]


@pytest.mark.parametrize(
    "data",
    [
        (["predecessor", 0]),
        (["successor", -1]),
    ],
)
def test_conected_lane_section_getter(data):
    jc = xodr.CommonJunctionCreator(100, "my_junction")
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, data[0])
    jc._get_connecting_lane_section(0) == data[1]


@pytest.fixture()
def lane_def_fixture():
    def create_junction(r1_connection, r2_connection):
        junction_creator_direct = xodr.CommonJunctionCreator(
            id=400, name="second_highway_connection"
        )
        road1 = xodr.create_road(
            xodr.Line(100),
            1,
            left_lanes=xodr.LaneDef(20, 80, 2, 2, None, [1, 2], [3, 4]),
            right_lanes=xodr.LaneDef(20, 80, 2, 2, None, [5, 6], [7, 8]),
        )
        road2 = xodr.create_road(
            xodr.Line(100),
            2,
            left_lanes=xodr.LaneDef(20, 80, 2, 2, None, [9, 10], [11, 12]),
            right_lanes=xodr.LaneDef(20, 80, 2, 2, None, [13, 14], [15, 16]),
        )
        junction_creator_direct.add_incoming_road_cartesian_geometry(
            road1, 0, 0, 0, r1_connection
        )
        junction_creator_direct.add_incoming_road_cartesian_geometry(
            road2, 0, 20, np.pi, r2_connection
        )
        return junction_creator_direct

    return create_junction


@pytest.mark.parametrize(
    "data",
    [
        (["successor", "predecessor", [3, 4], [9, 10], [7, 8], [13, 14]]),
        (["successor", "successor", [3, 4], [15, 16], [7, 8], [11, 12]]),
        (["predecessor", "successor", [5, 6], [15, 16], [1, 2], [11, 12]]),
        (["predecessor", "predecessor", [5, 6], [9, 10], [1, 2], [13, 14]]),
    ],
)
def test_lane_def_creator(lane_def_fixture, data):
    junction_creator_direct = lane_def_fixture(data[0], data[1])
    left_lane_defs, right_lane_defs = junction_creator_direct._get_lane_defs(0, 1, 20)
    assert left_lane_defs.n_lanes_start == 2
    assert left_lane_defs.n_lanes_end == 2
    assert left_lane_defs.s_start == 0
    assert left_lane_defs.s_end == 20
    assert left_lane_defs.lane_start_widths == data[2]
    assert left_lane_defs.lane_end_widths == data[3]

    assert right_lane_defs.n_lanes_start == 2
    assert right_lane_defs.n_lanes_end == 2
    assert right_lane_defs.s_start == 0
    assert right_lane_defs.s_end == 20
    assert right_lane_defs.lane_start_widths == data[4]
    assert right_lane_defs.lane_end_widths == data[5]


def test_lane_def_unequal_lanes():
    junction_creator_direct = xodr.CommonJunctionCreator(
        id=400, name="second_highway_connection"
    )
    road1 = xodr.create_road(
        xodr.Line(100),
        1,
        left_lanes=xodr.LaneDef(20, 80, 2, 2, None, [1, 2], [3, 4]),
        right_lanes=xodr.LaneDef(20, 80, 2, 2, None, [5, 6], [7, 8]),
    )
    road2 = xodr.create_road(
        xodr.Line(100),
        2,
        left_lanes=xodr.LaneDef(20, 80, 1, 1, None, [9], [11]),
        right_lanes=xodr.LaneDef(20, 80, 1, 1, None, [13], [15]),
    )
    junction_creator_direct.add_incoming_road_cartesian_geometry(
        road1, 0, 0, 0, "successor"
    )
    junction_creator_direct.add_incoming_road_cartesian_geometry(
        road2, 0, 20, np.pi, "predecessor"
    )

    left_lane_defs, right_lane_defs = junction_creator_direct._get_lane_defs(
        0, 1, 20, True
    )
    assert left_lane_defs.n_lanes_start == 1
    assert left_lane_defs.n_lanes_end == 1
    assert left_lane_defs.s_start == 0
    assert left_lane_defs.s_end == 20
    assert left_lane_defs.lane_start_widths == [3.0]
    assert left_lane_defs.lane_end_widths == [9.0]

    assert right_lane_defs.n_lanes_start == 1
    assert right_lane_defs.n_lanes_end == 1
    assert right_lane_defs.s_start == 0
    assert right_lane_defs.s_end == 20
    assert right_lane_defs.lane_start_widths == [7.0]
    assert right_lane_defs.lane_end_widths == [13.0]


def test_equal_connections():
    road1 = xodr.create_road(xodr.Line(100), 1, 2, 2)
    road2 = xodr.create_road(xodr.Line(100), 2, 2, 2)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, "successor")
    jc.add_incoming_road_cartesian_geometry(road2, 20, 0, np.pi, "predecessor")
    jc.add_connection(1, 2)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert len(conn_road.lanes.lanesections[0].leftlanes) == 2
    assert len(conn_road.lanes.lanesections[0].rightlanes) == 2


def test_unequal_connections():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, "successor")
    jc.add_incoming_road_cartesian_geometry(road2, 20, 0, np.pi, "predecessor")
    jc.add_connection(1, 2)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert len(conn_road.lanes.lanesections[0].leftlanes) == 2
    assert len(conn_road.lanes.lanesections[0].rightlanes) == 1


def test_connection_with_laneinput_leftlanes_no_suc_pred():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_circular_geometry(road1, 10, 0, "successor")
    jc.add_incoming_road_circular_geometry(road2, 10, np.pi, "predecessor")
    jc.add_connection(1, 2, 1, 1)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert len(conn_road.lanes.lanesections[0].leftlanes) == 1
    assert len(conn_road.lanes.lanesections[0].rightlanes) == 0


def test_connection_with_laneinput_rightlanes_no_suc_pred():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, "successor")
    jc.add_incoming_road_cartesian_geometry(road2, 20, 0, np.pi, "predecessor")
    jc.add_connection(1, 2, -1, -1)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert len(conn_road.lanes.lanesections[0].leftlanes) == 0
    assert len(conn_road.lanes.lanesections[0].rightlanes) == 1


def test_connection_with_laneinput_rightlanes_suc_pred_wrong_input():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, "successor")
    jc.add_incoming_road_cartesian_geometry(road2, 20, 0, np.pi, "predecessor")
    with pytest.raises(xodr.exceptions.MixingDrivingDirection) as e:
        jc.add_connection(1, 2, -1, 1)


def test_connection_with_laneinput_leftlanes_no_pred_pred():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_circular_geometry(road1, 10, 0, "predecessor")
    jc.add_incoming_road_circular_geometry(road2, 10, np.pi, "predecessor")
    jc.add_connection(1, 2, 1, -1)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert len(conn_road.lanes.lanesections[0].leftlanes) == 0
    assert len(conn_road.lanes.lanesections[0].rightlanes) == 1


def test_connection_with_laneinput_rightlanes_no_pred_pred():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_circular_geometry(road1, 10, 0, "predecessor")
    jc.add_incoming_road_circular_geometry(road2, 10, np.pi, "predecessor")
    jc.add_connection(1, 2, -1, 1)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert len(conn_road.lanes.lanesections[0].leftlanes) == 1
    assert len(conn_road.lanes.lanesections[0].rightlanes) == 0


def test_connection_with_laneinput_rightlanes_pred_pred_wrong_input():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_incoming_road_cartesian_geometry(road1, 0, 0, 0, "predecessor")
    jc.add_incoming_road_cartesian_geometry(road2, 20, 0, np.pi, "predecessor")
    with pytest.raises(xodr.exceptions.MixingDrivingDirection) as e:
        jc.add_connection(1, 2, 1, 1)


def test_elevation_before_road_creation():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")
    jc.add_constant_elevation(1)
    jc.add_incoming_road_circular_geometry(road1, 10, 0, "predecessor")
    jc.add_incoming_road_circular_geometry(road2, 10, np.pi, "predecessor")
    jc.add_connection(1, 2, -1, 1)
    conn_road = jc.junction_roads[0]
    assert conn_road.planview.get_total_length() == 20

    assert conn_road.elevationprofile.elevations[0].a == 1


def test_elevation_after_road_creation():
    road1 = xodr.create_road(xodr.Line(100), 1, left_lanes=2, right_lanes=2)
    road2 = xodr.create_road(xodr.Line(100), 2, left_lanes=2, right_lanes=1)
    jc = xodr.CommonJunctionCreator(100, "my junc")

    jc.add_incoming_road_circular_geometry(road1, 10, 0, "predecessor")
    jc.add_incoming_road_circular_geometry(road2, 10, np.pi, "predecessor")
    jc.add_connection(1, 2, -1, 1)
    jc.add_constant_elevation(1.0)
    conn_road = jc.junction_roads[0]

    assert conn_road.elevationprofile.elevations[0].a == 1.0


@pytest.fixture
def direct_junction_left_lane_fixture():
    junction_creator_direct = xodr.DirectJunctionCreator(
        id=400, name="second_highway_connection"
    )

    main_road = xodr.create_road(xodr.Line(200), 1, right_lanes=3, left_lanes=3)
    small_road = xodr.create_road(xodr.Line(200), 2, right_lanes=0, left_lanes=1)

    return main_road, small_road, junction_creator_direct


def test_direct_junction_offsets_pre_suc_1_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(small_road, main_road, 1, 3)

    assert main_road.pred_direct_junction == {small_road.id: -2}
    assert small_road.succ_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (1, 3)


def test_direct_junction_offsets_pre_suc_2_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road, 3, 1)

    assert main_road.pred_direct_junction == {small_road.id: -2}
    assert small_road.succ_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (3, 1)


def test_direct_junction_offsets_pre_suc_3_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road)

    assert main_road.pred_direct_junction == {small_road.id: 0}
    assert small_road.succ_direct_junction == {main_road.id: 0}
    assert junction_creator.junction.connections[0].links[0] == (1, 1)


def test_direct_junction_offsets_suc_pre_1_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, 1, 3)
    assert main_road.succ_direct_junction == {small_road.id: -2}
    assert small_road.pred_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (1, 3)


def test_direct_junction_offsets_suc_pre_2_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, 3, 1)
    assert main_road.succ_direct_junction == {small_road.id: -2}
    assert small_road.pred_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (3, 1)


def test_direct_junction_offsets_suc_pre_3_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road)
    assert main_road.succ_direct_junction == {small_road.id: 0}
    assert small_road.pred_direct_junction == {main_road.id: 0}
    assert junction_creator.junction.connections[0].links[0] == (1, 1)


def test_direct_junction_offsets_suc_suc_1_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, 1, -3)
    assert main_road.succ_direct_junction == {small_road.id: 2}
    assert small_road.succ_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (1, -3)


def test_direct_junction_offsets_suc_suc_2_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, -3, 1)
    assert main_road.succ_direct_junction == {small_road.id: 2}
    assert small_road.succ_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (-3, 1)


def test_direct_junction_offsets_pre_pre_1_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, 1, -3)
    assert main_road.pred_direct_junction == {small_road.id: 2}
    assert small_road.pred_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (1, -3)


def test_direct_junction_offsets_pre_pre_2_left(direct_junction_left_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_left_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, -3, 1)
    assert main_road.pred_direct_junction == {small_road.id: 2}
    assert small_road.pred_direct_junction == {main_road.id: 2}
    assert junction_creator.junction.connections[0].links[0] == (-3, 1)


@pytest.fixture
def direct_junction_right_lane_fixture():
    junction_creator_direct = xodr.DirectJunctionCreator(
        id=400, name="second_highway_connection"
    )

    main_road = xodr.create_road(xodr.Line(200), 1, right_lanes=3, left_lanes=3)
    small_road = xodr.create_road(xodr.Line(200), 2, right_lanes=1, left_lanes=0)

    return main_road, small_road, junction_creator_direct


def test_direct_junction_offsets_pre_suc_1_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(small_road, main_road, -1, -3)

    assert main_road.pred_direct_junction == {small_road.id: 2}
    assert small_road.succ_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (-1, -3)


def test_direct_junction_offsets_pre_suc_2_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road, -3, -1)

    assert main_road.pred_direct_junction == {small_road.id: 2}
    assert small_road.succ_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (-3, -1)


def test_direct_junction_offsets_pre_suc_3_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road)

    assert main_road.pred_direct_junction == {small_road.id: 0}
    assert small_road.succ_direct_junction == {main_road.id: 0}
    assert junction_creator.junction.connections[0].links[0] == (-1, -1)


def test_direct_junction_offsets_suc_pre_1_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, -1, -3)
    assert main_road.succ_direct_junction == {small_road.id: 2}
    assert small_road.pred_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (-1, -3)


def test_direct_junction_offsets_suc_pre_2_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, -3, -1)
    assert main_road.succ_direct_junction == {small_road.id: 2}
    assert small_road.pred_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (-3, -1)


def test_direct_junction_offsets_suc_pre_3_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road)
    assert main_road.succ_direct_junction == {small_road.id: 0}
    assert small_road.pred_direct_junction == {main_road.id: 0}
    assert junction_creator.junction.connections[0].links[0] == (-1, -1)


def test_direct_junction_offsets_suc_suc_1_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, -1, 3)
    assert main_road.succ_direct_junction == {small_road.id: -2}
    assert small_road.succ_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (-1, 3)


def test_direct_junction_offsets_suc_suc_2_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, 3, -1)
    assert main_road.succ_direct_junction == {small_road.id: -2}
    assert small_road.succ_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (3, -1)


def test_direct_junction_offsets_pre_pre_1_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, -1, 3)
    assert main_road.pred_direct_junction == {small_road.id: -2}
    assert small_road.pred_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (-1, 3)


def test_direct_junction_offsets_pre_pre_2_right(direct_junction_right_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_right_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, 3, -1)
    assert main_road.pred_direct_junction == {small_road.id: -2}
    assert small_road.pred_direct_junction == {main_road.id: -2}
    assert junction_creator.junction.connections[0].links[0] == (3, -1)


# multilane offset checks


@pytest.fixture
def direct_junction_left_multi_lane_fixture():
    junction_creator_direct = xodr.DirectJunctionCreator(
        id=400, name="second_highway_connection"
    )

    main_road = xodr.create_road(xodr.Line(200), 1, right_lanes=3, left_lanes=3)
    small_road = xodr.create_road(xodr.Line(200), 2, right_lanes=0, left_lanes=1)

    return main_road, small_road, junction_creator_direct


def test_direct_junction_offsets_pre_suc_1_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(small_road, main_road, [1, 2], [2, 3])

    assert main_road.pred_direct_junction == {small_road.id: -1}
    assert small_road.succ_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (1, 3)


def test_direct_junction_offsets_pre_suc_2_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road, [2, 3], [1, 2])

    assert main_road.pred_direct_junction == {small_road.id: -1}
    assert small_road.succ_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (3, 1)


def test_direct_junction_offsets_suc_pre_1_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [1, 2], [2, 3])
    assert main_road.succ_direct_junction == {small_road.id: -1}
    assert small_road.pred_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (1, 3)


def test_direct_junction_offsets_suc_pre_2_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [2, 3], [1, 2])
    assert main_road.succ_direct_junction == {small_road.id: -1}
    assert small_road.pred_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (3, 1)


def test_direct_junction_offsets_suc_suc_1_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [1, 2], [-2, -3])
    assert main_road.succ_direct_junction == {small_road.id: 1}
    assert small_road.succ_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (1, -3)


def test_direct_junction_offsets_suc_suc_2_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [-2, -3], [1, 2])
    assert main_road.succ_direct_junction == {small_road.id: 1}
    assert small_road.succ_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (-3, 1)


def test_direct_junction_offsets_pre_pre_1_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [1, 2], [-2, -3])
    assert main_road.pred_direct_junction == {small_road.id: 1}
    assert small_road.pred_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (1, -3)


def test_direct_junction_offsets_pre_pre_2_left(
    direct_junction_left_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_left_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [-2, -3], [1, 2])
    assert main_road.pred_direct_junction == {small_road.id: 1}
    assert small_road.pred_direct_junction == {main_road.id: 1}
    # assert junction_creator.junction.connections[0].links[0] == (-3, 1)


@pytest.fixture
def direct_junction_right_multi_lane_fixture():
    junction_creator_direct = xodr.DirectJunctionCreator(
        id=400, name="second_highway_connection"
    )

    main_road = xodr.create_road(xodr.Line(200), 1, right_lanes=3, left_lanes=3)
    small_road = xodr.create_road(xodr.Line(200), 2, right_lanes=2, left_lanes=0)

    return main_road, small_road, junction_creator_direct


def test_direct_junction_offsets_pre_suc_1_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(small_road, main_road, [-1, -2], [-2, -3])

    assert main_road.pred_direct_junction == {small_road.id: 1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (-1, -2)
    assert junction_creator.junction.connections[0].links[1] == (-2, -3)


def test_direct_junction_offsets_pre_suc_1_right_wrong_input(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    with pytest.raises(xodr.exceptions.MixingDrivingDirection) as e:
        junction_creator.add_connection(small_road, main_road, [1, 2], [-2, -3])


def test_direct_junction_offsets_pre_suc_2_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road, [-2, -3], [-1, -2])

    assert main_road.pred_direct_junction == {small_road.id: 1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (-2, -1)
    assert junction_creator.junction.connections[0].links[1] == (-3, -2)


def test_direct_junction_offsets_suc_pre_1_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [-1, -2], [-2, -3])
    assert main_road.succ_direct_junction == {small_road.id: 1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (-1, -2)
    assert junction_creator.junction.connections[0].links[1] == (-2, -3)


def test_direct_junction_offsets_suc_pre_2_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [-2, -3], [-1, -2])
    assert main_road.succ_direct_junction == {small_road.id: 1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (-2, -1)
    assert junction_creator.junction.connections[0].links[1] == (-3, -2)


def test_direct_junction_offsets_suc_suc_1_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [-1, -2], [2, 3])
    assert main_road.succ_direct_junction == {small_road.id: -1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (-1, 2)
    assert junction_creator.junction.connections[0].links[1] == (-2, 3)


def test_direct_junction_offsets_suc_suc_1_right_wrong_input(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    with pytest.raises(xodr.exceptions.MixingDrivingDirection) as e:
        junction_creator.add_connection(small_road, main_road, [-1, -2], [2, 3])


def test_direct_junction_offsets_suc_suc_2_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [2, 3], [-1, -2])
    assert main_road.succ_direct_junction == {small_road.id: -1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (2, -1)
    assert junction_creator.junction.connections[0].links[1] == (3, -2)


def test_direct_junction_offsets_pre_pre_1_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [-1, -2], [2, 3])
    assert main_road.pred_direct_junction == {small_road.id: -1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (-1, 2)
    assert junction_creator.junction.connections[0].links[1] == (-2, 3)


def test_direct_junction_offsets_pre_pre_2_right(
    direct_junction_right_multi_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [2, 3], [-1, -2])
    assert main_road.pred_direct_junction == {small_road.id: -1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    assert junction_creator.junction.connections[0].links[0] == (2, -1)
    assert junction_creator.junction.connections[0].links[1] == (3, -2)


@pytest.fixture
def direct_junction_both_lane_fixture():
    junction_creator_direct = xodr.DirectJunctionCreator(
        id=400, name="second_highway_connection"
    )

    main_road = xodr.create_road(xodr.Line(200), 1, right_lanes=3, left_lanes=3)
    small_road = xodr.create_road(xodr.Line(200), 2, right_lanes=1, left_lanes=1)

    return main_road, small_road, junction_creator_direct


def test_direct_junction_minimum_connection_pre_suc(direct_junction_both_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_both_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road)
    assert len(junction_creator.junction.connections) == 1
    assert len(junction_creator.junction.connections[0].links) == 2
    assert junction_creator.junction.connections[0].links[0] == (-1, -1)
    assert junction_creator.junction.connections[0].links[1] == (1, 1)


def test_direct_junction_minimum_connection_suc_pred(direct_junction_both_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_both_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road)
    assert len(junction_creator.junction.connections) == 1
    assert len(junction_creator.junction.connections[0].links) == 2
    assert junction_creator.junction.connections[0].links[0] == (-1, -1)
    assert junction_creator.junction.connections[0].links[1] == (1, 1)


def test_direct_junction_minimum_connection_suc_suc(direct_junction_both_lane_fixture):
    main_road, small_road, junction_creator = direct_junction_both_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road)
    assert len(junction_creator.junction.connections) == 1
    assert len(junction_creator.junction.connections[0].links) == 2
    assert junction_creator.junction.connections[0].links[0] == (1, -1)
    assert junction_creator.junction.connections[0].links[1] == (-1, 1)


def test_direct_junction_minimum_connection_pred_pred(
    direct_junction_both_lane_fixture,
):
    main_road, small_road, junction_creator = direct_junction_both_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road)
    assert len(junction_creator.junction.connections) == 1
    assert len(junction_creator.junction.connections[0].links) == 2
    assert junction_creator.junction.connections[0].links[0] == (1, -1)
    assert junction_creator.junction.connections[0].links[1] == (-1, 1)
