import pytest


import openscenario as OSC


TD = OSC.TransitionDynamics('step',0,'rate',1)


def test_speedaction_abs():
    speedaction = OSC.SpeedAction(TD)
    speedaction.set_absolute_target_speed(50)
    with pytest.raises(ValueError):
        speedaction.set_relative_target_speed(1,'Ego')
    OSC.prettyprint(speedaction.get_element())

def test_speedaction_rel():
    speedaction = OSC.SpeedAction(TD)
    speedaction.set_relative_target_speed(1,'Ego')
    with pytest.raises(ValueError):
        speedaction.set_absolute_target_speed(50)
    OSC.prettyprint(speedaction.get_element())


def test_longdistaction_dist():
    longdist = OSC.LongitudinalDistanceAction('Ego')
    longdist.set_distance(1)
    with pytest.raises(ValueError):
        longdist.set_timegap(1)
    longdist.get_attributes()

    OSC.prettyprint(longdist.get_element())


def test_longdistaction_time():
    longdist = OSC.LongitudinalDistanceAction('Ego',max_acceleration=1)
    longdist.set_timegap(1)
    with pytest.raises(ValueError):
        longdist.set_distance(1)
    longdist.get_attributes()

    OSC.prettyprint(longdist.get_element())



def test_lanechange_noinp():
    lanechange = OSC.LaneChangeAction(TD)
    lanechange.set_absolute_target_lane(1)

    OSC.prettyprint(lanechange.get_element())

def test_lanechange_inp():
    lanechange = OSC.LaneChangeAction(TD,0.2)
    lanechange.set_absolute_target_lane(1)
    OSC.prettyprint(lanechange.get_element())

def test_lanechange_rel():
    lanechange = OSC.LaneChangeAction(TD,0.2)
    lanechange.set_relative_target_lane(1,'Ego')
    OSC.prettyprint(lanechange.get_element())



def test_laneoffset_abs():
    laneoffset = OSC.LaneOffsetAction('step',0,3)
    laneoffset.set_absolute_target_lane(1)
    OSC.prettyprint(laneoffset.get_element())

def test_laneoffset_rel():
    laneoffset = OSC.LaneOffsetAction('step',0,3)
    laneoffset.set_relative_target_lane(1,'Ego')
    OSC.prettyprint(laneoffset.get_element())

def test_lateraldistance_noconst():
    latdist = OSC.LateralDistanceAction('Ego')
    OSC.prettyprint(latdist.get_element())

def test_lateraldistance_const():
    latdist = OSC.LateralDistanceAction('Ego',3,max_speed=50)
    OSC.prettyprint(latdist.get_element())

def test_teleport():
    teleport = OSC.TeleportAction(OSC.WorldPosition())
    OSC.prettyprint(teleport.get_element())





