import pytest


from scenariogeneration import xosc as OSC
from scenariogeneration import prettyprint
from scenariogeneration.xosc.exceptions import NoActionsDefinedError

TD = OSC.TransitionDynamics(OSC.DynamicsShapes.step,OSC.DynamicsDimension.rate,1)


def test_speedaction_abs():
    speedaction = OSC.AbsoluteSpeedAction(50,TD)
    prettyprint(speedaction.get_element())

def test_speedaction_rel():
    speedaction = OSC.RelativeSpeedAction(1,'Ego',TD)

    prettyprint(speedaction.get_element())

def test_longdistaction_dist():
    longdist = OSC.LongitudinalDistanceAction(1,'Ego')
    prettyprint(longdist.get_element())

def test_longdistaction_time():
    longdist = OSC.LongitudinalTimegapAction(2,'Ego',max_acceleration=1)
    prettyprint(longdist.get_element())

def test_lanechange_abs():
    lanechange = OSC.AbsoluteLaneChangeAction(1,TD)
    prettyprint(lanechange.get_element())

def test_lanechange_rel():
    lanechange = OSC.RelativeLaneChangeAction(1,'Ego',TD,0.2)
    prettyprint(lanechange.get_element())

def test_laneoffset_abs():
    laneoffset = OSC.AbsoluteLaneOffsetAction(1,OSC.DynamicsShapes.step,3,False)
    prettyprint(laneoffset.get_element())

def test_laneoffset_rel():
    laneoffset = OSC.RelativeLaneOffsetAction(1,'Ego',OSC.DynamicsShapes.step,3,False)
    prettyprint(laneoffset.get_element())

def test_lateraldistance_noconst():
    latdist = OSC.LateralDistanceAction('Ego')
    prettyprint(latdist.get_element())

def test_lateraldistance_const():
    latdist = OSC.LateralDistanceAction('Ego',3,max_speed=50)
    prettyprint(latdist.get_element())

def test_teleport():
    teleport = OSC.TeleportAction(OSC.WorldPosition())
    prettyprint(teleport.get_element())

def test_assign_route():
    route = OSC.Route('myroute')
    route.add_waypoint(OSC.WorldPosition(0,0,0,0,0,0),OSC.RouteStrategy.shortest)
    route.add_waypoint(OSC.WorldPosition(1,1,0,0,0,0),OSC.RouteStrategy.shortest)
    OSC.AssignRouteAction(route)

def test_aqcuire_position_route():
    ara = OSC.AcquirePositionAction(OSC.WorldPosition(1,1,0,0,0,0))
    prettyprint(ara.get_element())

def test_activate_controller_action():
    aca = OSC.ActivateControllerAction(True,True)
    prettyprint(aca.get_element())


def test_assign_controller_action():
    prop = OSC.Properties()
    prop.add_property('mything','2')
    prop.add_property('theotherthing','true')

    cnt = OSC.Controller('mycontroller',prop)
    
    
    aca = OSC.AssignControllerAction(cnt)
    prettyprint(aca.get_element())

def test_override_controller():
    ocva = OSC.OverrideControllerValueAction()
    with pytest.raises(NoActionsDefinedError):
        ocva.get_element()
    ocva.set_brake(True,2)
    prettyprint(ocva.get_element())
    ocva.set_throttle(False,0)
    prettyprint(ocva.get_element())
    ocva.set_clutch(True,1)
    prettyprint(ocva.get_element())
    ocva.set_parkingbrake(False,1)
    prettyprint(ocva.get_element())
    ocva.set_steeringwheel(True,1)
    prettyprint(ocva.get_element())
    ocva.set_gear(False,0)
    prettyprint(ocva.get_element())
def test_visual_action():
    va = OSC.VisibilityAction(True,False,True)
    prettyprint(va.get_element())

def test_abs_sync_action():
    
    asa = OSC.AbsoluteSynchronizeAction('Ego',OSC.WorldPosition(0,0,0,0,0,0),OSC.WorldPosition(10,0,0,0,0,0),20)
    prettyprint(asa.get_element())

def test_rel_sync_action():
    
    asa = OSC.RelativeSynchronizeAction('Ego',OSC.WorldPosition(0,0,0,0,0,0),OSC.WorldPosition(10,0,0,0,0,0),20,'delta')
    prettyprint(asa.get_element())


def test_follow_traj_action_polyline():

    positionlist = []
    positionlist.append(OSC.RelativeLanePosition(10,0.5,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,1,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,-1,-3,'Ego'))
    positionlist.append(OSC.RelativeLanePosition(10,0,-3,'Ego'))
    prettyprint(positionlist[0].get_element())
    polyline = OSC.Polyline([0,0.5,1,1.5],positionlist)


    traj = OSC.Trajectory('my_trajectory',False)
    traj.add_shape(polyline)

    trajact = OSC.FollowTrajectoryAction(traj,OSC.FollowMode.position)
    prettyprint(trajact.get_element())


def testParameterAddActions():
    prettyprint(OSC.ParameterAddAction('Myparam',3).get_element())

def testParameterMultiplyActions():
    prettyprint(OSC.ParameterMultiplyAction('Myparam',3).get_element())

def testParameterSetActions():
    prettyprint(OSC.ParameterSetAction('Myparam',3).get_element())

def test_trafficsignalstateaction():
    prettyprint(OSC.TrafficSignalStateAction('my signal','red').get_element())


def test_addEntity():
    prettyprint(OSC.AddEntityAction('my new thingy',OSC.WorldPosition()).get_element())

def test_deleteEntity():
    prettyprint(OSC.DeleteEntityAction('my new thingy').get_element())

def test_trafficsourceaction():
    
    prop = OSC.Properties()
    prop.add_file('mycontrollerfile.xml')
    controller = OSC.Controller('mycontroller',prop)

    traffic = OSC.TrafficDefinition('my traffic')
    traffic.add_controller(controller,0.5)
    traffic.add_controller(OSC.CatalogReference('ControllerCatalog','my controller'),0.5)

    traffic.add_vehicle(OSC.VehicleCategory.car,0.9)
    traffic.add_vehicle(OSC.VehicleCategory.bicycle,0.1)

    source_action = OSC.TrafficSourceAction(10,10,OSC.WorldPosition(),traffic,100)

    prettyprint(source_action.get_element())

    source_action = OSC.TrafficSourceAction(10,10,OSC.WorldPosition(),traffic)
    prettyprint(source_action.get_element())


def test_trafficsinkaction():
    
    prop = OSC.Properties()
    prop.add_file('mycontrollerfile.xml')
    controller = OSC.Controller('mycontroller',prop)

    traffic = OSC.TrafficDefinition('my traffic')
    traffic.add_controller(controller,0.5)
    traffic.add_controller(OSC.CatalogReference('ControllerCatalog','my controller'),0.5)

    traffic.add_vehicle(OSC.VehicleCategory.car,0.9)
    traffic.add_vehicle(OSC.VehicleCategory.bicycle,0.1)

    sink_action = OSC.TrafficSinkAction(10,10,OSC.WorldPosition(),traffic)
    prettyprint(sink_action.get_element())


    
def test_trafficswarmaction():
    
    prop = OSC.Properties()
    prop.add_file('mycontrollerfile.xml')
    controller = OSC.Controller('mycontroller',prop)

    traffic = OSC.TrafficDefinition('my traffic')
    traffic.add_controller(controller,0.5)
    traffic.add_controller(OSC.CatalogReference('ControllerCatalog','my controller'),0.5)

    traffic.add_vehicle(OSC.VehicleCategory.car,0.9)
    traffic.add_vehicle(OSC.VehicleCategory.bicycle,0.1)

    source_action = OSC.TrafficSourceAction(10,10,OSC.WorldPosition(),traffic,100)

    prettyprint(source_action.get_element())

    swarm_action = OSC.TrafficSwarmAction(10,20,10,2,10,'Ego',traffic)
    prettyprint(swarm_action.get_element())

    swarm_action = OSC.TrafficSwarmAction(10,20,10,2,10,'Ego',traffic,10)
    prettyprint(swarm_action.get_element())


def test_environmentaction():
    tod = OSC.TimeOfDay(True,2020,10,1,18,30,30)
    weather = OSC.Weather(OSC.CloudState.free,100,0,1,OSC.PrecipitationType.dry,1)
    rc = OSC.RoadCondition(1)

    env = OSC.Environment(tod,weather,rc)
    ea = OSC.EnvironmentAction('myaction',env)
    prettyprint(ea.get_element())