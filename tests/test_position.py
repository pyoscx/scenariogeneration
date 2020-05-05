
import pytest

import openscenario as OSC

def test_worldposition_noinput():
    pos = OSC.WorldPosition()
    pos.get_attributes()
    p = pos.get_element()
    OSC.prettyprint(p)

def test_worldposition_input():
    pos = OSC.WorldPosition(x=1,y=2,z=1.123)
    pos.get_attributes()
    p = pos.get_element()
    OSC.prettyprint(p)


def test_relativeworldposition():
    
    pos = OSC.RelativePosition('Ego',1,2,reference='world')
    OSC.prettyprint(pos.get_element())

    pos = OSC.RelativePosition('Target',1,2,3,orientation=OSC.Orientation(h=0.2))
    OSC.prettyprint(pos.get_element())


def test_relativeobjectposition():
    
    pos = OSC.RelativePosition('Ego',1,2,reference='object')
    OSC.prettyprint(pos.get_element())

    pos = OSC.RelativePosition('Target',1,2,3,orientation=OSC.Orientation(h=0.2))
    OSC.prettyprint(pos.get_element())


def test_roadposition():
    pos = OSC.RoadPosition(1,2,reference_id='1',reference='road')
    OSC.prettyprint(pos.get_element())

    pos = OSC.RoadPosition(1,2,reference_id='Ego',reference='object')
    OSC.prettyprint(pos.get_element())

def test_laneposition():
    pos = OSC.LanePosition(1,2,lane='lane1',reference='road',reference_id='road1')
    OSC.prettyprint(pos.get_element())

    pos = OSC.LanePosition(1,2,lane=1,reference='object',reference_id='Ego')
    OSC.prettyprint(pos.get_element())