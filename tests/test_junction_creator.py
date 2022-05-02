
import pytest
from scenariogeneration import xodr
from scenariogeneration import prettyprint


@pytest.mark.parametrize(
    "data",
    [
        (['predecessor', 'successor', -1, 1, 1, -1]),
    ],
)
def test_create_straight_road(data):
    junction_creator = xodr.JunctionCreator(id = 100, name = 'my_junction',startnum=100)
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

    # road = pyodrx.generators.create_straight_road(
    #     data[0], length=data[1], junction=data[2], n_lanes=data[3], lane_offset=data[4]
    # )
    # odr = pyodrx.OpenDrive("myroad")
    # odr.add_road(road)
    # odr.adjust_roads_and_lanes()

    # redict = road.get_attributes()

    # assert int(redict["id"]) == data[0]
    # assert int(redict["length"]) == data[1]
    # assert int(redict["junction"]) == data[2]
    # assert len(road.lanes.lanesections[0].leftlanes) == data[3]
    # assert len(road.lanes.lanesections[0].rightlanes) == data[3]
    # assert road.lanes.lanesections[0].leftlanes[0].a == data[4]
    # assert road.lanes.lanesections[0].leftlanes[0].b == 0
    # assert road.lanes.lanesections[0].leftlanes[0].c == 0
    # assert road.lanes.lanesections[0].leftlanes[0].d == 0

