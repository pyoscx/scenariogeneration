import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint


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
    # assert junction_creator.junction.connections[0].links[0] == (-1, -3)


def test_direct_junction_offsets_pre_suc_2_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    junction_creator.add_connection(main_road, small_road, [-2, -3], [-1, -2])

    assert main_road.pred_direct_junction == {small_road.id: 1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (-3, -1)


def test_direct_junction_offsets_suc_pre_1_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [-1, -2], [-2, -3])
    assert main_road.succ_direct_junction == {small_road.id: 1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (-1, -3)


def test_direct_junction_offsets_suc_pre_2_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [-2, -3], [-1, -2])
    assert main_road.succ_direct_junction == {small_road.id: 1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (-3, -1)


def test_direct_junction_offsets_suc_suc_1_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [-1, -2], [2, 3])
    assert main_road.succ_direct_junction == {small_road.id: -1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (-1, 3)


def test_direct_junction_offsets_suc_suc_2_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_successor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_successor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [2, 3], [-1, -2])
    assert main_road.succ_direct_junction == {small_road.id: -1}
    assert small_road.succ_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (3, -1)


def test_direct_junction_offsets_pre_pre_1_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(small_road, main_road, [-1, -2], [2, 3])
    assert main_road.pred_direct_junction == {small_road.id: -1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (-1, 3)


def test_direct_junction_offsets_pre_pre_2_right(
    direct_junction_right_multi_lane_fixture,
):

    main_road, small_road, junction_creator = direct_junction_right_multi_lane_fixture
    main_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)
    small_road.add_predecessor(xodr.ElementType.junction, junction_creator.id)

    junction_creator.add_connection(main_road, small_road, [2, 3], [-1, -2])
    assert main_road.pred_direct_junction == {small_road.id: -1}
    assert small_road.pred_direct_junction == {main_road.id: -1}
    # assert junction_creator.junction.connections[0].links[0] == (3, -1)
