import pytest


import pyoscx as OSC


TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.rate,1)


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
    laneoffset = OSC.AbsoluteLaneOffsetAction(1,OSC.DynamicsShapes.step,0,3)
    OSC.prettyprint(laneoffset.get_element())

def test_laneoffset_rel():
    laneoffset = OSC.RelativeLaneOffsetAction(1,'Ego',OSC.DynamicsShapes.step,0,3)
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
    route.add_waypoint(OSC.WorldPosition(0,0,0,0,0,0),OSC.RouteStrategy.shortest)
    route.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),OSC.RouteStrategy.shortest)
    OSC.AssingRouteAction(route)

def test_aqcuire_position_route():
    ara = OSC.AssingRouteAction(OSC.WorldPosition(1,1,0,0,0,0))
    OSC.prettyprint(ara.get_element())

def test_activate_controller_action():
    aca = OSC.ActivateControllerAction(True,True)
    OSC.prettyprint(aca.get_element())


def test_assign_controller_action():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroller',prop)
    
    
    aca = OSC.AssignControllerAction(cnt)
    OSC.prettyprint(aca.get_element())

def test_overide_brake():
    oa = OSC.OverrideBrakeAction(0.4,True)
    OSC.prettyprint(oa.get_element())

def test_overide_clutch():
    oa = OSC.OverrideClutchAction(0.4,True)
    OSC.prettyprint(oa.get_element())

def test_overide_parking():
    oa = OSC.OverrideParkingBrakeAction(0.4,True)
    OSC.prettyprint(oa.get_element())

def test_overide_gear():
    oa = OSC.OverrideGearAction(0.4,True)
    OSC.prettyprint(oa.get_element())

def test_overide_steering():
    oa = OSC.OverrideSteeringWheelAction(0.4,True)
    OSC.prettyprint(oa.get_element())

def test_overide_throttle():
    oa = OSC.OverrideThrottleAction(0.4,True)
    OSC.prettyprint(oa.get_element())

def test_visual_action():
    va = OSC.VisibilityAction(True,False,True)
    OSC.prettyprint(va.get_element())

def test_abs_sync_action():
    
    asa = OSC.AbsoluteSynchronizeAction('Ego',OSC.WorldPosition(0,0,0,0,0,0),OSC.WorldPosition(10,0,0,0,0,0),20)
    OSC.prettyprint(asa.get_element())

def test_rel_sync_action():
    
    asa = OSC.RelativeSynchronizeAction('Ego',OSC.WorldPosition(0,0,0,0,0,0),OSC.WorldPosition(10,0,0,0,0,0),20,'delta')
    OSC.prettyprint(asa.get_element())


def test_follow_traj_action_polyline():

    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,-1,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,0,-3,'Ego'))
    OSC.prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0,0.5,1,1.5],positionlist)


    traj = OSC.Trajectory('my_trajectory','False')
    traj.add_shape(polyline)

    trajact = OSC.FollowTrajectoryAction(traj,OSC.FollowMode.position)
    OSC.prettyprint(trajact.get_element())