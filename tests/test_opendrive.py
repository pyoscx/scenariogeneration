import pytest


import pyodrx 


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

    pyodrx.prettyprint(road.get_element())


    
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
    pyodrx.prettyprint(road.get_element())