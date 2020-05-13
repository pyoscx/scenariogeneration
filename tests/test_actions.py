import pytest


import pyoscx as OSC


TD = OSC.TransitionDynamics('step','rate',1)


def test_speedaction_abs():
    speedaction = OSC.AbsoluteSpeedAction(50,TD)
    OSC.prettyprint(speedaction.get_element())

def test_speedaction_rel():
    speedaction = OSC.RelativeSpeedAction(1,'Ego',TD)

    OSC.prettyprint(speedaction.get_element())


def test_longdistaction_dist():
    longdist = OSC.LongitudinalDistanceAction(1,'Ego')
    OSC.prettyprint(longdist.get_element())


def test_longdistaction_time():
    longdist = OSC.LongitudinalTimegapAction(2,'Ego',max_acceleration=1)
    OSC.prettyprint(longdist.get_element())



def test_lanechange_abs():
    lanechange = OSC.AbsoluteLaneChangeAction(1,TD)
    OSC.prettyprint(lanechange.get_element())

def test_lanechange_rel():
    lanechange = OSC.RelativeLaneChangeAction(1,'Ego',TD,0.2)
    OSC.prettyprint(lanechange.get_element())

def test_laneoffset_abs():
    laneoffset = OSC.AbsoluteLaneOffsetAction(1,'step',0,3)
    OSC.prettyprint(laneoffset.get_element())

def test_laneoffset_rel():
    laneoffset = OSC.RelativeLaneOffsetAction(1,'Ego','step',0,3)
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

def test_assign_route():
    route = OSC.Route('myroute')
    route.add_waypoint(OSC.WorldPosition(0,0,0,0,0,0),'closest')
    route.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),'closest')
    OSC.AssingRouteAction(route)

def test_aqcuire_position_route():
    ara = OSC.AssingRouteAction(OSC.WorldPosition(1,1,0,0,0,0))
    OSC.prettyprint(ara.get_element())

def test_activate_controller_action():
    aca = OSC.ActivateControllerAction(True,True)
    OSC.prettyprint(aca.get_element())