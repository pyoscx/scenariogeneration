import pytest


from scenariogeneration import xodr as pyodrx
from scenariogeneration import prettyprint
def test_roadline():
    line = pyodrx.RoadLine()
    
    prettyprint(line.get_element())
    line = pyodrx.RoadLine(1,2,3,5,1,pyodrx.MarkRule.no_passing,pyodrx.RoadMarkColor.standard)
    prettyprint(line.get_element())


def test_roadmark():
    mark = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2)
    prettyprint(mark.get_element())
    mark = pyodrx.RoadMark(pyodrx.RoadMarkType.solid,0.2,1,1,1,pyodrx.MarkRule.no_passing,pyodrx.RoadMarkColor.standard)
    prettyprint(mark.get_element())

def test_lane():
    lane = pyodrx.Lane()
    lane._set_lane_id(1)
    prettyprint(lane.get_element())
    lane = pyodrx.Lane(pyodrx.LaneType.driving,1,1,1,1,2)
    lane._set_lane_id(1)
    prettyprint(lane.get_element())
    
def test_lane_with_height():
    lane = pyodrx.Lane(pyodrx.LaneType.sidewalk,1,1,1,1,2)
    lane._set_lane_id(1)
    lane.add_height(0.15)
    prettyprint(lane.get_element())

def test_lanesection():
    centerlane = pyodrx.Lane()
    ls = pyodrx.LaneSection(0,centerlane)
    prettyprint(ls.get_element())
    right_lane = pyodrx.Lane()
    ls.add_right_lane(right_lane)
    prettyprint(ls.get_element())
    left_lane = pyodrx.Lane(a=2)
    ls.add_left_lane(left_lane)
    prettyprint(ls.get_element())

def test_lanes():
    centerlane = pyodrx.Lane()
    ls = pyodrx.LaneSection(0,centerlane)
    lanes = pyodrx.Lanes()
    lanes.add_lanesection(ls)
    prettyprint(lanes.get_element())