
import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint


@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', -1, -1 ]),
        (['successor', 'predecessor', -1, -1 ]),
        (['successor', 'successor', -1, 1 ]),
        (['predecessor', 'predecessor', -1, 1 ]),
    ],
)
def test_connection_single_right_lane_to_dobule_lane(data):
    junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=0,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', 1, 1 ]),
        (['successor', 'predecessor', 1, 1 ]),
        (['successor', 'successor', 1, -1 ]),
        (['predecessor', 'predecessor', 1, -1 ]),
    ],
)
def test_connections_single_left_lane_to_double(data):
    junction_creator = xodr.JunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=1,right_lanes=0)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]

@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', 1, 1 ]),
        (['successor', 'predecessor', 1, 1 ]),
        (['successor', 'successor', -1, 1 ]),
        (['predecessor', 'predecessor', -1, 1 ]),
    ],
)
def test_connections_double_to_single_left_lane(data):
    junction_creator = xodr.JunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=1,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=0)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]

@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', -1, -1 ]),
        (['successor', 'predecessor', -1, -1 ]),
        (['successor', 'successor', -1, 1 ]),
        (['predecessor', 'predecessor', -1, 1 ]),
    ],
)
def test_connections_double_to_single_right_lane(data):
    junction_creator = xodr.JunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=0,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', 1, 1 ]),
        (['successor', 'predecessor', 1, 1 ]),
        (['successor', 'successor', 1, -1 ]),
        (['predecessor', 'predecessor', 1, -1 ]),
    ],
)
def test_connections_single_left_lane_to_double(data):
    junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=1,right_lanes=0)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]

@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', 1, 1 ]),
        (['successor', 'predecessor', 1, 1 ]),
        (['successor', 'successor', -1, 1 ]),
        (['predecessor', 'predecessor', -1, 1 ]),
    ],
)
def test_connections_double_to_single_left_lane(data):
    junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=1,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=0)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]

@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', -1, -1 ]),
        (['successor', 'predecessor', -1, -1 ]),
        (['successor', 'successor', -1, 1 ]),
        (['predecessor', 'predecessor', -1, 1 ]),
    ],
)
def test_connections_double_to_single_right_lane(data):
    junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=0,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes[0] == data[2]
    assert r2_lanes[0] == data[3]


@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', [1, -1], [1, -1]]),
        (['successor', 'predecessor', [1, -1], [1, -1]]),
        (['successor', 'successor', [1, -1], [-1, 1]  ]),
        (['predecessor', 'predecessor', [1, -1], [-1, 1] ]),
    ],
)
def test_connections_left_and_right(data):
    junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=1,right_lanes=1)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=1,right_lanes=1)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes == data[2]
    assert r2_lanes == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes == data[3]
    assert r2_lanes == data[2]
    

@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', [1, 2, -1, -2], [1,2, -1, -2]]),
        (['successor', 'predecessor', [1, 2, -1, -2], [1, 2, -1, -2]]),
        (['successor', 'successor', [1, 2, -1, -2], [-1, -2, 1, 2]  ]),
        (['predecessor', 'predecessor', [1, 2, -1, -2], [-1, -2, 1, 2] ]),
    ],
)
def test_connections_4lanes(data):
    junction_creator = xodr.CommonJunctionCreator(id = 100, name = 'my_junction',startnum=100)
    road1 = xodr.create_road(xodr.Line(100),1,left_lanes=2,right_lanes=2)
    road2 = xodr.create_road(xodr.Arc(0.01,100),2, left_lanes=2,right_lanes=2)

    junction_creator.add_incoming_road_circular_geometry(road1,20,0, road_connection = data[0])
    junction_creator.add_incoming_road_circular_geometry(road2,20,3, road_connection = data[1])
    

    (r1_lanes, r2_lanes) = junction_creator._get_minimum_lanes_to_connect(road1,road2)
    assert r1_lanes == data[2]
    assert r2_lanes == data[3]
    (r2_lanes, r1_lanes) = junction_creator._get_minimum_lanes_to_connect(road2,road1)
    assert r1_lanes == data[3]
    assert r2_lanes == data[2]
