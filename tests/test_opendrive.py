import pytest
from scenariogeneration import xodr as pyodrx
from scenariogeneration import prettyprint

def test_simple_road():
    line1 = pyodrx.Line(100)
    planview = pyodrx.PlanView()
    planview.add_geometry(line1)

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)


    lane1 = pyodrx.Lane(a=2)
    lane1.add_roadmark(rm)
    lanesec = pyodrx.LaneSection(0,lane1)

    lanes = pyodrx.Lanes()
    lanes.add_lanesection(lanesec)

    road = pyodrx.Road(1,planview,lanes)

    prettyprint(road.get_element())


    
def test_link_road():
    line1 = pyodrx.Line(100)
    planview = pyodrx.PlanView()
    planview.add_geometry(line1)

    rm = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,rule=pyodrx.MarkRule.no_passing)


    lane1 = pyodrx.Lane(a=2)
    lane1.add_roadmark(rm)
    lanesec = pyodrx.LaneSection(0,lane1)

    lanes = pyodrx.Lanes()
    lanes.add_lanesection(lanesec)

    road = pyodrx.Road(1,planview,lanes)
    road.add_predecessor(pyodrx.ElementType.road,'1',pyodrx.ContactPoint.start)
    prettyprint(road.get_element())


@pytest.mark.parametrize("data",[\
([10, 100,-1,1, 3]),
([10, 50,-1,1, 3]),
([10, 100,1,1, 3]),
([10, 100,-1,2, 3]),
([10, 100,-1,10, 3]),
([10, 100,-1,10, 5]),
])

def test_create_straight_road(data): 

    road = pyodrx.generators.create_straight_road(data[0], length=data[1], junction=data[2], n_lanes=data[3], lane_offset=data[4])
    odr = pyodrx.OpenDrive('myroad')
    odr.add_road(road)
    odr.adjust_roads_and_lanes()

    redict = road.get_attributes()

    assert int(redict['id']) == data[0]
    assert int(redict['length']) == data[1]
    assert int(redict['junction']) == data[2]
    assert len(road.lanes.lanesections[0].leftlanes) == data[3]
    assert len(road.lanes.lanesections[0].rightlanes) == data[3]
    assert road.lanes.lanesections[0].leftlanes[0].a == data[4]
    assert road.lanes.lanesections[0].leftlanes[0].b == 0
    assert road.lanes.lanesections[0].leftlanes[0].c == 0
    assert road.lanes.lanesections[0].leftlanes[0].d == 0
    

def test_road_type():
    rt = pyodrx.opendrive._Type(pyodrx.RoadType.motorway,0,'SE')
    prettyprint(rt.get_element())

    rt = pyodrx.opendrive._Type(pyodrx.RoadType.motorway,0,'SE',speed='no limit')
    prettyprint(rt.get_element())

def test_road_with_road_types():
    road = pyodrx.create_straight_road(0)
    road.add_type(pyodrx.RoadType.motorway,0)
    prettyprint(road.get_element())